# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Schedule'
        db.create_table('workshop_schedule', (
            ('tag_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['qpool.Tag'], unique=True, primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 2, 22, 0, 0))),
            ('end_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 2, 22, 0, 0))),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=3)),
        ))
        db.send_create_signal('workshop', ['Schedule'])

        # Adding model 'WorkshopPlayer'
        db.create_table('workshop_workshopplayer', (
            ('player_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['user.Player'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('workshop', ['WorkshopPlayer'])

        # Adding model 'Semigroup'
        db.create_table('workshop_semigroup', (
            ('playergroup_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['user.PlayerGroup'], unique=True, primary_key=True)),
            ('day', self.gf('django.db.models.fields.IntegerField')()),
            ('hour', self.gf('django.db.models.fields.IntegerField')()),
            ('room', self.gf('django.db.models.fields.CharField')(default='eg306', max_length=5, blank=True)),
        ))
        db.send_create_signal('workshop', ['Semigroup'])

        # Adding unique constraint on 'Semigroup', fields ['day', 'hour', 'room']
        db.create_unique('workshop_semigroup', ['day', 'hour', 'room'])

        # Adding model 'Workshop'
        db.create_table('workshop_workshop', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('semigroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workshop.Semigroup'])),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 2, 22, 0, 0))),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True)),
            ('start_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('active_until', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('question_count', self.gf('django.db.models.fields.IntegerField')(default=3, blank=True)),
        ))
        db.send_create_signal('workshop', ['Workshop'])

        # Adding model 'Assessment'
        db.create_table('workshop_assessment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('workshop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workshop.Workshop'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assessments', to=orm['user.Player'])),
            ('answered', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('time_start', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('time_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('grade', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('reviewer_grade', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('final_grade', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('workshop', ['Assessment'])

        # Adding M2M table for field questions on 'Assessment'
        m2m_table_name = db.shorten_name('workshop_assessment_questions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('assessment', models.ForeignKey(orm['workshop.assessment'], null=False)),
            ('question', models.ForeignKey(orm['qpool.question'], null=False))
        ))
        db.create_unique(m2m_table_name, ['assessment_id', 'question_id'])

        # Adding M2M table for field reviewers on 'Assessment'
        m2m_table_name = db.shorten_name('workshop_assessment_reviewers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('assessment', models.ForeignKey(orm['workshop.assessment'], null=False)),
            ('player', models.ForeignKey(orm['user.player'], null=False))
        ))
        db.create_unique(m2m_table_name, ['assessment_id', 'player_id'])

        # Adding model 'Answer'
        db.create_table('workshop_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('assessment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workshop.Assessment'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wsanswers', to=orm['qpool.Question'])),
            ('text', self.gf('django.db.models.fields.TextField')(max_length=2000)),
            ('grade', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('workshop', ['Answer'])

        # Adding model 'Review'
        db.create_table('workshop_review', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('answer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['workshop.Answer'])),
            ('reviewer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['user.Player'])),
            ('feedback', self.gf('django.db.models.fields.TextField')(max_length=2000, null=True, blank=True)),
            ('answer_grade', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('review_reviewer', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='reviews', null=True, to=orm['user.Player'])),
            ('review_grade', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('workshop', ['Review'])


    def backwards(self, orm):
        # Removing unique constraint on 'Semigroup', fields ['day', 'hour', 'room']
        db.delete_unique('workshop_semigroup', ['day', 'hour', 'room'])

        # Deleting model 'Schedule'
        db.delete_table('workshop_schedule')

        # Deleting model 'WorkshopPlayer'
        db.delete_table('workshop_workshopplayer')

        # Deleting model 'Semigroup'
        db.delete_table('workshop_semigroup')

        # Deleting model 'Workshop'
        db.delete_table('workshop_workshop')

        # Deleting model 'Assessment'
        db.delete_table('workshop_assessment')

        # Removing M2M table for field questions on 'Assessment'
        db.delete_table(db.shorten_name('workshop_assessment_questions'))

        # Removing M2M table for field reviewers on 'Assessment'
        db.delete_table(db.shorten_name('workshop_assessment_reviewers'))

        # Deleting model 'Answer'
        db.delete_table('workshop_answer')

        # Deleting model 'Review'
        db.delete_table('workshop_review')


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
        'game.game': {
            'Meta': {'object_name': 'Game'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'magic.artifact': {
            'Meta': {'unique_together': "(('name', 'group', 'percents'),)", 'object_name': 'Artifact'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['magic.ArtifactGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'percents': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'magic.artifactgroup': {
            'Meta': {'object_name': 'ArtifactGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'magic.groupartifactamount': {
            'Meta': {'unique_together': "(('group', 'artifact'),)", 'object_name': 'GroupArtifactAmount'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'artifact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magic.Artifact']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.PlayerGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'magic.playerartifactamount': {
            'Meta': {'unique_together': "(('player', 'artifact'),)", 'object_name': 'PlayerArtifactAmount'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'artifact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magic.Artifact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Player']"})
        },
        'magic.playerspellamount': {
            'Meta': {'unique_together': "(('player', 'spell'),)", 'object_name': 'PlayerSpellAmount'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Player']"}),
            'spell': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magic.Spell']"})
        },
        'magic.raceartifactamount': {
            'Meta': {'unique_together': "(('race', 'artifact'),)", 'object_name': 'RaceArtifactAmount'},
            'amount': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'artifact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['magic.Artifact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Race']"})
        },
        'magic.spell': {
            'Meta': {'object_name': 'Spell'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'due_days': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'level_required': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'mass': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'percents': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '10'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'o'", 'max_length': '1'})
        },
        'qpool.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'qpool.question': {
            'Meta': {'object_name': 'Question'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'answer_type': ('django.db.models.fields.CharField', [], {'default': "'R'", 'max_length': '1'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['qpool.Category']", 'null': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'endorsed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'qpool_question_endorsedby_related'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'proposed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'qpool_question_proposedby_related'", 'null': 'True', 'to': "orm['auth.User']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['qpool.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'S'", 'max_length': '1'})
        },
        'qpool.tag': {
            'Meta': {'object_name': 'Tag'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['qpool.Category']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'user.player': {
            'Meta': {'object_name': 'Player'},
            'artifacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['magic.Artifact']", 'symmetrical': 'False', 'through': "orm['magic.PlayerArtifactAmount']", 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '600', 'blank': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'level_no': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'max_level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'nickname': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '20', 'null': 'True'}),
            'points': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['user.Race']", 'null': 'True'}),
            'spells_collection': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'spell_collection'", 'blank': 'True', 'through': "orm['magic.PlayerSpellAmount']", 'to': "orm['magic.Spell']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'player_related'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'user.playergroup': {
            'Meta': {'object_name': 'PlayerGroup'},
            'artifacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['magic.Artifact']", 'symmetrical': 'False', 'through': "orm['magic.GroupArtifactAmount']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['game.Game']", 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['user.Race']", 'null': 'True', 'blank': 'True'}),
            'players': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['user.Player']", 'symmetrical': 'False', 'blank': 'True'}),
            'points': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'})
        },
        'user.race': {
            'Meta': {'object_name': 'Race'},
            'artifacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['magic.Artifact']", 'symmetrical': 'False', 'through': "orm['magic.RaceArtifactAmount']", 'blank': 'True'}),
            'can_play': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'})
        },
        'workshop.answer': {
            'Meta': {'object_name': 'Answer'},
            'assessment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workshop.Assessment']"}),
            'grade': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wsanswers'", 'to': "orm['qpool.Question']"}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '2000'})
        },
        'workshop.assessment': {
            'Meta': {'object_name': 'Assessment'},
            'answered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'final_grade': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'grade': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assessments'", 'to': "orm['user.Player']"}),
            'questions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['qpool.Question']", 'symmetrical': 'False', 'blank': 'True'}),
            'reviewer_grade': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reviewers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'assessments_review'", 'blank': 'True', 'to': "orm['user.Player']"}),
            'time_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'time_start': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'workshop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workshop.Workshop']"})
        },
        'workshop.review': {
            'Meta': {'object_name': 'Review'},
            'answer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workshop.Answer']"}),
            'answer_grade': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'feedback': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'review_grade': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'review_reviewer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reviews'", 'null': 'True', 'to': "orm['user.Player']"}),
            'reviewer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user.Player']"})
        },
        'workshop.schedule': {
            'Meta': {'object_name': 'Schedule', '_ormbases': ['qpool.Tag']},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'end_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 2, 22, 0, 0)'}),
            'start_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 2, 22, 0, 0)'}),
            'tag_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['qpool.Tag']", 'unique': 'True', 'primary_key': 'True'})
        },
        'workshop.semigroup': {
            'Meta': {'unique_together': "(('day', 'hour', 'room'),)", 'object_name': 'Semigroup', '_ormbases': ['user.PlayerGroup']},
            'day': ('django.db.models.fields.IntegerField', [], {}),
            'hour': ('django.db.models.fields.IntegerField', [], {}),
            'playergroup_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['user.PlayerGroup']", 'unique': 'True', 'primary_key': 'True'}),
            'room': ('django.db.models.fields.CharField', [], {'default': "'eg306'", 'max_length': '5', 'blank': 'True'})
        },
        'workshop.workshop': {
            'Meta': {'object_name': 'Workshop'},
            'active_until': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2014, 2, 22, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question_count': ('django.db.models.fields.IntegerField', [], {'default': '3', 'blank': 'True'}),
            'semigroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['workshop.Semigroup']"}),
            'start_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'})
        },
        'workshop.workshopplayer': {
            'Meta': {'object_name': 'WorkshopPlayer', '_ormbases': ['user.Player']},
            'player_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['user.Player']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['workshop']