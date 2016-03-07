# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('qpool_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('qpool', ['Category'])

        # Adding model 'Tag'
        db.create_table('qpool_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['qpool.Category'], null=True, blank=True)),
        ))
        db.send_create_signal('qpool', ['Tag'])

        # Adding model 'Question'
        db.create_table('qpool_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')(default='')),
            ('rich_text', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
            ('proposed_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='qpool_question_proposedby_related', null=True, to=orm['auth.User'])),
            ('endorsed_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='qpool_question_endorsedby_related', null=True, to=orm['auth.User'])),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['qpool.Category'], null=True)),
            ('answer_type', self.gf('django.db.models.fields.CharField')(default='C', max_length=1)),
            ('type', self.gf('django.db.models.fields.CharField')(default='S', max_length=1)),
            ('code', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_changed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('qpool', ['Question'])

        # Adding M2M table for field tags on 'Question'
        m2m_table_name = db.shorten_name('qpool_question_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('question', models.ForeignKey(orm['qpool.question'], null=False)),
            ('tag', models.ForeignKey(orm['qpool.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['question_id', 'tag_id'])

        # Adding model 'Answer'
        db.create_table('qpool_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['qpool.Question'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('rich_text', self.gf('ckeditor.fields.RichTextField')(null=True, blank=True)),
            ('explanation', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('correct', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('qpool', ['Answer'])

        # Adding model 'Schedule'
        db.create_table('qpool_schedule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.OneToOneField')(related_name='schedule', unique=True, to=orm['qpool.Question'])),
            ('day', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now, blank=True)),
        ))
        db.send_create_signal('qpool', ['Schedule'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table('qpool_category')

        # Deleting model 'Tag'
        db.delete_table('qpool_tag')

        # Deleting model 'Question'
        db.delete_table('qpool_question')

        # Removing M2M table for field tags on 'Question'
        db.delete_table(db.shorten_name('qpool_question_tags'))

        # Deleting model 'Answer'
        db.delete_table('qpool_answer')

        # Deleting model 'Schedule'
        db.delete_table('qpool_schedule')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'qpool.answer': {
            'Meta': {'object_name': 'Answer'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'explanation': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['qpool.Question']"}),
            'rich_text': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'qpool.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'qpool.question': {
            'Meta': {'object_name': 'Question'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'answer_type': ('django.db.models.fields.CharField', [], {'default': "'C'", 'max_length': '1'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['qpool.Category']", 'null': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'endorsed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'qpool_question_endorsedby_related'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'proposed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'qpool_question_proposedby_related'", 'null': 'True', 'to': "orm['auth.User']"}),
            'rich_text': ('ckeditor.fields.RichTextField', [], {'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['qpool.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'S'", 'max_length': '1'})
        },
        'qpool.schedule': {
            'Meta': {'object_name': 'Schedule'},
            'day': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'schedule'", 'unique': 'True', 'to': "orm['qpool.Question']"})
        },
        'qpool.tag': {
            'Meta': {'object_name': 'Tag'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['qpool.Category']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['qpool']