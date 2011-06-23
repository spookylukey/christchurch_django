# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Speaker'
        db.create_table('sermons_speaker', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('sermons', ['Speaker'])

        # Adding model 'Topic'
        db.create_table('sermons_topic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('sermons', ['Topic'])

        # Adding model 'Series'
        db.create_table('sermons_series', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal('sermons', ['Series'])

        # Adding model 'Sermon'
        db.create_table('sermons_sermon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sermon', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
            ('speaker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sermons.Speaker'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('bible_book', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('passage', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sermons.Series'], null=True, blank=True)),
            ('date_delivered', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('time_delivered', self.gf('django.db.models.fields.TimeField')(db_index=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('sermons', ['Sermon'])

        # Adding M2M table for field topics on 'Sermon'
        db.create_table('sermons_sermon_topics', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sermon', models.ForeignKey(orm['sermons.sermon'], null=False)),
            ('topic', models.ForeignKey(orm['sermons.topic'], null=False))
        ))
        db.create_unique('sermons_sermon_topics', ['sermon_id', 'topic_id'])


    def backwards(self, orm):
        
        # Deleting model 'Speaker'
        db.delete_table('sermons_speaker')

        # Deleting model 'Topic'
        db.delete_table('sermons_topic')

        # Deleting model 'Series'
        db.delete_table('sermons_series')

        # Deleting model 'Sermon'
        db.delete_table('sermons_sermon')

        # Removing M2M table for field topics on 'Sermon'
        db.delete_table('sermons_sermon_topics')


    models = {
        'sermons.series': {
            'Meta': {'ordering': "['name']", 'object_name': 'Series'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'sermons.sermon': {
            'Meta': {'ordering': "['-date_delivered', 'time_delivered']", 'object_name': 'Sermon'},
            'bible_book': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'date_delivered': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'passage': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sermons.Series']", 'null': 'True', 'blank': 'True'}),
            'sermon': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sermons.Speaker']"}),
            'time_delivered': ('django.db.models.fields.TimeField', [], {'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sermons.Topic']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'sermons.speaker': {
            'Meta': {'ordering': "['name']", 'object_name': 'Speaker'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'sermons.topic': {
            'Meta': {'ordering': "['name']", 'object_name': 'Topic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['sermons']
