from django.db import models
from uuid import uuid4
import qrcode
import qrcode.image.svg
from weasyprint import HTML, CSS


css = CSS(string="""
    @page {
		size: A4;
		margin: 0;
	}
    body {
        margin: 0;
        width: 100%;
        height: 100%;
        background-size: cover;
    }
    p {
        font-family: arial, sans-serif;
        position: absolute;
        text-align: center;
        overflow: hidden;
        /*border: 1px solid red;*/
    }
    p.first_name {
        top: 16cm;
        left: 4cm;
        right: 4cm;
        height: 2cm;
        font-size: 4em;
    }
    p.last_name {
        top: 19cm;
        left: 4cm;
        right: 4cm;
        height: 2cm;
        font-size: 4em;
        text-transform: uppercase;
    }
    p.title {
        top: 24cm;
        left: 4cm;
        right: 4cm;
        height: 4cm;
        font-size: 2em;
    }
    svg {
        position: absolute;
        right: 4cm;
        top: 4cm;
        width: 2cm;
        height: 2cm;
    }
""")


class Category(models.Model):
    name = models.CharField(max_length=100)
    background = models.FileField()

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Badge(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    key = models.UUIDField(default=uuid4, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    catering_guest = models.OneToOneField("catering.Guest", on_delete=models.SET_NULL, null=True, blank=True)

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
        return html.render(stylesheets=[css])
