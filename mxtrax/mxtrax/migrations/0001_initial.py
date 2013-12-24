# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Customer'
        db.create_table(u'mxtrax_customer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('codename', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('friendlyname', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'mxtrax', ['Customer'])

        # Adding model 'MailDomain'
        db.create_table(u'mxtrax_maildomain', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('domainname', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('testuser', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('failing', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('maintmode', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mxtrax.Customer'])),
        ))
        db.send_create_signal(u'mxtrax', ['MailDomain'])

        # Adding model 'MailTest'
        db.create_table(u'mxtrax_mailtest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('testid', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('sendtime', self.gf('django.db.models.fields.DateTimeField')()),
            ('receivetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('receiveheaders', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True)),
            ('maildomain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mxtrax.MailDomain'])),
            ('incl_in_stat', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'mxtrax', ['MailTest'])

        # Adding model 'Config'
        db.create_table(u'mxtrax_config', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sendinguser', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True, null=True)),
            ('maxreturntime', self.gf('django.db.models.fields.IntegerField')(default=300)),
            ('alertuser', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True, null=True)),
            ('mboxpath', self.gf('django.db.models.fields.CharField')(max_length=2048, unique=True, null=True)),
            ('maxfailnumber', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('maxfailpercentage', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('maxlatenumber', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('maxlatepercentage', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('max_sec_until_fail', self.gf('django.db.models.fields.IntegerField')(default=86400)),
        ))
        db.send_create_signal(u'mxtrax', ['Config'])

        # Adding model 'Stat'
        db.create_table(u'mxtrax_stat', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('d', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('min_delivery_time', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('max_delivery_time', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('domain', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mxtrax.MailDomain'])),
            ('ontime_num', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('late_num', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('fail_num', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('total_num', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('all_done', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('total_delivery_time', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'mxtrax', ['Stat'])


    def backwards(self, orm):
        # Deleting model 'Customer'
        db.delete_table(u'mxtrax_customer')

        # Deleting model 'MailDomain'
        db.delete_table(u'mxtrax_maildomain')

        # Deleting model 'MailTest'
        db.delete_table(u'mxtrax_mailtest')

        # Deleting model 'Config'
        db.delete_table(u'mxtrax_config')

        # Deleting model 'Stat'
        db.delete_table(u'mxtrax_stat')


    models = {
        u'mxtrax.config': {
            'Meta': {'object_name': 'Config'},
            'alertuser': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_sec_until_fail': ('django.db.models.fields.IntegerField', [], {'default': '86400'}),
            'maxfailnumber': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'maxfailpercentage': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'maxlatenumber': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'maxlatepercentage': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'maxreturntime': ('django.db.models.fields.IntegerField', [], {'default': '300'}),
            'mboxpath': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'unique': 'True', 'null': 'True'}),
            'sendinguser': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True', 'null': 'True'})
        },
        u'mxtrax.customer': {
            'Meta': {'object_name': 'Customer'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'friendlyname': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'mxtrax.maildomain': {
            'Meta': {'object_name': 'MailDomain'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mxtrax.Customer']"}),
            'domainname': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'failing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maintmode': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'testuser': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'mxtrax.mailtest': {
            'Meta': {'object_name': 'MailTest'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incl_in_stat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'maildomain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mxtrax.MailDomain']"}),
            'receiveheaders': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True'}),
            'receivetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sendtime': ('django.db.models.fields.DateTimeField', [], {}),
            'testid': ('django.db.models.fields.CharField', [], {'max_length': '36'})
        },
        u'mxtrax.stat': {
            'Meta': {'object_name': 'Stat'},
            'all_done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'd': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mxtrax.MailDomain']"}),
            'fail_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'late_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'max_delivery_time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_delivery_time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ontime_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_delivery_time': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_num': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['mxtrax']