# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Contact.include_on_email_lists'
        db.add_column('contacts_contact', 'include_on_email_lists', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Contact.include_on_email_lists'
        db.delete_column('contacts_contact', 'include_on_email_lists')


    models = {
        'contacts.contact': {
            'Meta': {'ordering': "['name']", 'object_name': 'Contact'},
            'address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'church_member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'home_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contacts.HomeGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_on_email_lists': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
