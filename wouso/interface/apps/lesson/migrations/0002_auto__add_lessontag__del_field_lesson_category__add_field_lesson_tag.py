# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LessonTag'
        db.create_table('lesson_lessontag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='tags', null=True, to=orm['lesson.LessonCategory'])),
        ))
        db.send_create_signal('lesson', ['LessonTag'])

        # Deleting field 'Lesson.category'
        db.delete_column('lesson_lesson', 'category_id')

        # Adding field 'Lesson.tag'
        db.add_column('lesson_lesson', 'tag',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='lessons', null=True, to=orm['lesson.LessonTag']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'LessonTag'
        db.delete_table('lesson_lessontag')


        # User chose to not deal with backwards NULL issues for 'Lesson.category'
        raise RuntimeError("Cannot reverse this migration. 'Lesson.category' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Lesson.category'
        db.add_column('lesson_lesson', 'category',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lesson.LessonCategory']),
                      keep_default=False)

        # Deleting field 'Lesson.tag'
        db.delete_column('lesson_lesson', 'tag_id')


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
            'content': ('ckeditor.fields.RichTextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'quiz': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quiz.Quiz']", 'null': 'True', 'blank': 'True'}),
            'quiz_show_time': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'lessons'", 'null': 'True', 'to': "orm['lesson.LessonTag']"}),
            'youtube_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'lesson.lessoncategory': {
            'Meta': {'object_name': 'LessonCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000', 'blank': 'True'})
        },
        'lesson.lessontag': {
            'Meta': {'object_name': 'LessonTag'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'tags'", 'null': 'True', 'to': "orm['lesson.LessonCategory']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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