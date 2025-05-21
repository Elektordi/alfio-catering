from django.db import models
from uuid import uuid4
import qrcode
import qrcode.image.svg
from weasyprint import HTML, CSS


default_css = """
@page {
	size: A4;
	margin: 0;
}
body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    background-size: contain;
    background-repeat: no-repeat;
}
p {
    margin: 0;
    padding: 0;
    font-family: arial, sans-serif;
    position: absolute;
    text-align: center;
    overflow: hidden;
    /*border: 1px solid red;*/
}
p.first_name {
    left: 105mm;
    right: 0mm;
    top: 86mm;
    height: 13mm;
    font-size: 3em;
    text-transform: uppercase;
    font-weight: bold;
}
p.last_name {
    left: 105mm;
    right: 0mm;
    top: 99mm;
    height: 18mm;
    font-size: 2em;
    text-transform: uppercase;
}
p.title {
    left: 105mm;
    right: 0mm;
    top: 123mm;
    height: 13mm;
    font-size: 1.5em;
    color: white;
    font-weight: bold;
    text-transform: uppercase;
}
svg {
    position: absolute;
    right: 5mm;
    top: 12mm;
    width: 25mm;
    height: 25mm;
}
""".strip()


class Category(models.Model):
    name = models.CharField(max_length=100)
    background = models.FileField()
    css = models.TextField(default=default_css)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Badge(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    shirt_size = models.CharField(max_length=10, blank=True)
    key = models.UUIDField(default=uuid4, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    catering_guest = models.OneToOneField("catering.Guest", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['first_name', 'last_name']]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.title})"

    def pdf(self):
        tag = qrcode.make(str(self.key), image_factory=qrcode.image.svg.SvgPathImage).to_string(encoding='unicode')
        html = HTML(string=f"""
        <body style="background-image: url('file://{self.category.background.path}')">
            <p class="first_name">{self.first_name}</p>
            <p class="last_name">{self.last_name}</p>
            <p class="title">{self.title}</p>
            {tag}
        </body>
        """)
        return html.render(stylesheets=[CSS(string=self.category.css)])

    def label_pdf(self):
        css = """
            @page {
	            size: A5;
	            margin: 0;
            }
            body {
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                background-size: contain;
                background-repeat: no-repeat;
            }
            .name {
                border: 1px solid black;
                width: 80%;
                margin-left: 10%;
                margin-top: 2cm;
            }
            p {
                font-size: 3em;
                font-family: arial, sans-serif;
                text-align: center;
            }
            p.last_name {
                font-weight: bold;
                text-transform: uppercase;
            }
            p.category {
                margin-top: 4cm;
            }
            p.title {
                margin-top: -1cm;
                font-size: 1em;
                font-style: italic;
            }
        """
        html = HTML(string=f"""
        <body>
            <div class="name">
                <p class="last_name">{self.last_name}</p>
                <p class="first_name">{self.first_name}</p>
            </div>
            <p class="category">{self.category.name}</p>
            <p class="title">{self.title}</p>
            <p class="shirt_size">{self.shirt_size}</p>
        </body>
        """)
        return html.render(stylesheets=[CSS(string=css)])

