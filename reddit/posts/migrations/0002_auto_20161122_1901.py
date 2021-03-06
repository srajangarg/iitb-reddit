from __future__ import unicode_literals		
		
from django.conf import settings		
from django.db import migrations, models		
import django.db.models.deletion		
		
		
class Migration(migrations.Migration):		
		
    initial = True		
		
    dependencies = [		
        ('subreddits', '0001_initial'),		
        ('posts', '0001_initial'),		
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),		
    ]		
		
    operations = [		
        migrations.AddField(		
            model_name='vote',		
            name='voted_by',		
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),		
        ),		
        migrations.AddField(		
            model_name='vote',		
            name='voted_on',		
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.Post'),		
        ),		
        migrations.AddField(		
            model_name='post',		
            name='posted_by',		
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),		
        ),		
        migrations.AddField(		
            model_name='textpost',		
            name='posted_in',		
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subreddits.Subreddit'),		
        ),		
        migrations.AddField(		
            model_name='linkpost',		
            name='posted_in',		
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subreddits.Subreddit'),		
        ),		
        migrations.AddField(		
            model_name='event',		
            name='posted_in',		
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='subreddits.Subreddit'),		
        ),		
        migrations.AddField(		
            model_name='comment',		
            name='commented_on',		
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_post', to='posts.Post'),		
        ),		
    ]