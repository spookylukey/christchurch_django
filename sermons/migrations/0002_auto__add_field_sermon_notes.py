# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Sermon.notes'
        db.add_column(u'sermons_sermon', 'notes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Sermon.notes'
        db.delete_column(u'sermons_sermon', 'notes')


    models = {
        u'sermons.series': {
            'Meta': {'ordering': "['name']", 'object_name': 'Series'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'sermons.sermon': {
            'Meta': {'ordering': "['-date_delivered', 'time_delivered']", 'object_name': 'Sermon'},
            'bible_book': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'date_delivered': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'passage': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sermons.Series']", 'null': 'True', 'blank': 'True'}),
            'sermon': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sermons.Speaker']"}),
            'time_delivered': ('django.db.models.fields.TimeField', [], {'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sermons.Topic']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'sermons.speaker': {
            'Meta': {'ordering': "['name']", 'object_name': 'Speaker'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'sermons.topic': {
            'Meta': {'ordering': "['name']", 'object_name': 'Topic'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['sermons']