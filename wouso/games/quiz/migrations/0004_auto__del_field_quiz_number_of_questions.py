# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Quiz.number_of_questions'
        db.delete_column('quiz_quiz', 'number_of_questions')


    def backwards(self, orm):
        # Adding field 'Quiz.number_of_questions'
        db.add_column('quiz_quiz', 'number_of_questions',
                      self.gf('django.db.models.fields.IntegerField')(default=5),
                      keep_default=False)


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
            'answer_type': ('django.db.models.fields.CharField', [], {'default': "'C'", 'max_length': '1'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['qpool.Category']", 'null': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'endorsed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'qpool_question_endorsedby_related'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'proposed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'qpool_question_proposedby_related'", 'null': 'True', 'to': "orm['auth.User']"}),
            'rich_text': ('ckeditor.fields.RichTextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['qpool.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'S'", 'max_length': '1'})
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
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quiz.QuizCategory']", 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'gold_reward': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['game.Game']", 'null': 'True', 'blank': 'True'}),
            'points_reward': ('django.db.models.fields.IntegerField', [], {'default': '100'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['qpool.Tag']", 'symmetrical': 'False'}),
            'time_limit': ('django.db.models.fields.IntegerField', [], {'default': '300'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'quiz.quizattempt': {
            'Meta': {'object_name': 'QuizAttempt'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'True', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'gold': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'points': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'results': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user_to_quiz': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'attempts'", 'null': 'True', 'to': "orm['quiz.UserToQuiz']"})
        },
        'quiz.quizcategory': {
            'Meta': {'object_name': 'QuizCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'quiz.quizuser': {
            'Meta': {'object_name': 'QuizUser', '_ormbases': ['user.Player']},
            'player_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['user.Player']", 'unique': 'True', 'primary_key': 'True'}),
            'quizzes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['quiz.Quiz']", 'through': "orm['quiz.UserToQuiz']", 'symmetrical': 'False'})
        },
        'quiz.usertoquiz': {
            'Meta': {'object_name': 'UserToQuiz'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'questions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['qpool.Question']", 'symmetrical': 'False'}),
            'quiz': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quiz.Quiz']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quiz.QuizUser']"})
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
        'user.race': {
            'Meta': {'object_name': 'Race'},
            'artifacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['magic.Artifact']", 'symmetrical': 'False', 'through': "orm['magic.RaceArtifactAmount']", 'blank': 'True'}),
            'can_play': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['quiz']