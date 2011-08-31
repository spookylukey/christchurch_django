# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'HomeGroup'
        db.create_table('contacts_homegroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('group_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
        ))
        db.send_create_signal('contacts', ['HomeGroup'])

        # Adding model 'Contact'
        db.create_table('contacts_contact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('post_code', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=22, blank=True)),
            ('mobile_number', self.gf('django.db.models.fields.CharField')(max_length=22, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('home_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contacts.HomeGroup'], null=True, blank=True)),
            ('church_member', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('contacts', ['Contact'])


    def backwards(self, orm):
        
        # Deleting model 'HomeGroup'
        db.delete_table('contacts_homegroup')

        # Deleting model 'Contact'
        db.delete_table('contacts_contact')


    models = {
        'contacts.contact': {
            'Meta': {'ordering': "['name']", 'object_name': 'Contact'},
            'address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'church_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'home_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contacts.HomeGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mobile_number': ('django.db.models.fields.CharField', [], {'max_length': '22', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '22', 'blank': 'True'}),
            'post_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'contacts.homegroup': {
            'Meta': {'ordering': "['name']", 'object_name': 'HomeGroup'},
            'group_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['contacts']
