# dans votre_app/signals.py

from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from .models import UniqueReference, RepairStore

@receiver(post_delete, sender=UniqueReference)
def create_new_unique_reference_after_delete(sender, instance, **kwargs):
    """
    Crée une nouvelle référence unique lorsque l'ancienne est supprimée,
    à condition que le nombre total de références non utilisées soit inférieur à 65.
    """
    current_references_count = UniqueReference.objects.filter(repairstore=instance.repairstore, is_used=False).count()

    if current_references_count < 65:
        create_new_unique_reference(instance.repairstore)

@receiver(pre_save, sender=UniqueReference)
def create_new_unique_reference_before_save(sender, instance, **kwargs):
    """
    Crée une nouvelle référence unique avant la sauvegarde si is_used est défini à True.
    """
    if instance.is_used:
        create_new_unique_reference(instance.repairstore)

def create_new_unique_reference(repairstore):
    """
    Fonction utilitaire pour créer une nouvelle référence unique non utilisée.
    """
    while True:
        new_reference_value = UniqueReference.generate_unique_reference_value()

        # Vérifier si la nouvelle référence n'est pas déjà attribuée à un utilisateur
        if not UniqueReference.objects.filter(value=new_reference_value).exists():
            UniqueReference.objects.create(repairstore=repairstore, value=new_reference_value)
            break

@receiver(post_save, sender=RepairStore)
def ensure_user_has_65_unique_references(sender, instance, created, **kwargs):
    if created:  # Vérifier si l'instance est nouvellement créée
        current_references_count = UniqueReference.objects.filter(repairstore=instance, is_used=False).count()

        if current_references_count < 65:
            for _ in range(65 - current_references_count):
                create_new_unique_reference(instance)
