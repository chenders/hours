from django.db import models

class Entry(models.Model):
    title = models.TextField()
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    verified = models.DateTimeField(null=True, blank=True)

    @property
    def seconds(self):
        return (self.end_time - self.start_time).total_seconds()

    def __unicode__(self):
        return '%s (%s -> %s)' % (self.title,
                                  self.start_time.strftime('%Y-%m-%d %H:%M'),
                                  self.end_time.strftime('%Y-%m-%d %H:%M'))

class Data(models.Model):
    date = models.DateTimeField(null=False)
    title = models.TextField()
    mouseover = models.TextField()
    url = models.TextField()
    css_class = models.TextField()

    class Meta:
        unique_together = (('date', 'title', 'url'),)
        ordering = ('date',)