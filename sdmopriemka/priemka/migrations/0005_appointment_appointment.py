# Generated by Django 4.2.20 on 2025-03-24 19:37

from django.db import migrations
import pgtrigger.compiler
import pgtrigger.migrations


class Migration(migrations.Migration):

    dependencies = [
        ('priemka', '0004_alter_appointment_appointment_status'),
    ]

    operations = [
        pgtrigger.migrations.AddTrigger(
            model_name='appointment',
            trigger=pgtrigger.compiler.Trigger(name='appointment', sql=pgtrigger.compiler.UpsertTriggerSql(func='UPDATE "priemka_appointment" SET is_archived = False WHERE "id" = OLD."id"; RETURN NULL;', hash='337c97a7cd8d3e355af546d6fcb440a985699277', operation='DELETE', pgid='pgtrigger_appointment_114ae', table='priemka_appointment', when='BEFORE')),
        ),
    ]
