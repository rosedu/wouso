# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Setting'
        db.create_table('config_setting', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('value', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
        ))
        db.send_create_signal('config', ['Setting'])

        # Adding model 'IntegerSetting'
        db.create_table('config_integersetting', (
            ('setting_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['config.Setting'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('config', ['IntegerSetting'])


    def backwards(self, orm):
        # Deleting model 'Setting'
        db.delete_table('config_setting')

        # Deleting model 'IntegerSetting'
        db.delete_table('config_integersetting')


    models = {
        'config.integersetting': {
            'Meta': {'object_name': 'IntegerSetting', '_ormbases': ['config.Setting']},
            'setting_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['config.Setting']", 'unique': 'True', 'primary_key': 'True'})
        },
        'config.setting': {
            'Meta': {'object_name': 'Setting'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['config']