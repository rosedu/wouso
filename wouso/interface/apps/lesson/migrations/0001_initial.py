# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LessonCategory'
        db.create_table('lesson_lessoncategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('order', self.gf('django.db.models.fields.CharField')(default='', max_length=1000, blank=True)),
        ))
        db.send_create_signal('lesson', ['LessonCategory'])

        # Adding model 'Lesson'
        db.create_table('lesson_lesson', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('youtube_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('content', self.gf('ckeditor.fields.RichTextField')()),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lesson.LessonCategory'])),
            ('quiz', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quiz.Quiz'], null=True, blank=True)),
            ('quiz_show_time', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('lesson', ['Lesson'])


    def backwards(self, orm):
        # Deleting model 'LessonCategory'
        db.delete_table('lesson_lessoncategory')

        # Deleting model 'Lesson'
        db.delete_table('lesson_lesson')


    models = {
        'game.game': {
            'Meta': {'object_name': 'Game'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'lesson.lesson': {
            'Meta': {'object_name': 'Lesson'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lesson.LessonCategory']"}),
            'content': ('ckeditor.fields.RichTextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'quiz': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quiz.Quiz']", 'null': 'True', 'blank': 'True'}),
            'quiz_show_time': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'youtube_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'lesson.lessoncategory': {
            'Meta': {'object_name': 'LessonCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'})
        },
        'qpool.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'qpool.tag': {
            'Meta': {'object_name': 'Tag'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['qpool.Category']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'quiz.quiz': {
            'Meta': {'object_name': 'Quiz'},
            'another_chance': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'gold_reward': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'number_of_questions': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['game.Game']", 'null': 'True', 'blank': 'True'}),
            'points_reward': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['qpool.Tag']", 'symmetrical': 'False'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {'default': '300'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        }
    }

    complete_apps = ['lesson']