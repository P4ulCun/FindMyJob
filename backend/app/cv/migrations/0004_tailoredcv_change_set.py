from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0003_add_coverletter'),
    ]

    operations = [
        migrations.AddField(
            model_name='tailoredcv',
            name='change_set',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='tailoredcv',
            name='original_education',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='tailoredcv',
            name='original_experience',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='tailoredcv',
            name='original_skills',
            field=models.JSONField(default=list),
        ),
    ]
