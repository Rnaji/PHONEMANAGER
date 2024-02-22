# dans votre_app/signals.py

from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from .models import UniqueReference, RepairStore, RecyclerPricing, BrokenScreen, ScreenModel
import logging

logger = logging.getLogger(__name__)

@receiver(post_delete, sender=UniqueReference)
def create_new_unique_reference_after_delete(sender, instance, **kwargs):
    if instance.repairstore:
        try:
            current_references_count = UniqueReference.objects.filter(repairstore=instance.repairstore, is_used=False).count()

            if current_references_count < 65:
                create_new_unique_reference(instance.repairstore)

        except Exception as e:
            logger.error(f"Error in create_new_unique_reference_after_delete: {e}", exc_info=True)


@receiver(pre_save, sender=UniqueReference)
def create_new_unique_reference_before_save(sender, instance, **kwargs):
    if instance.is_used and instance.repairstore:
        try:
            create_new_unique_reference(instance.repairstore)

        except Exception as e:
            logger.error(f"Error in create_new_unique_reference_before_save: {e}", exc_info=True)


def create_new_unique_reference(repairstore):
    """
    Fonction utilitaire pour créer une nouvelle référence unique non utilisée.
    """
    if repairstore:
        while True:
            new_reference_value = UniqueReference.generate_unique_reference_value()

            # Vérifier si la nouvelle référence n'est pas déjà attribuée à un utilisateur
            if not UniqueReference.objects.filter(value=new_reference_value).exists():
                UniqueReference.objects.create(repairstore=repairstore, value=new_reference_value)
                break


@receiver(post_save, sender=RepairStore)
def ensure_user_has_65_unique_references(sender, instance, created, **kwargs):
    if created and instance:  # Vérifiez si l'instance est nouvellement créée et non nulle
        try:
            current_references_count = UniqueReference.objects.filter(repairstore=instance, is_used=False).count()

            if current_references_count < 65:
                new_references = [
                    UniqueReference(repairstore=instance, value=UniqueReference.generate_unique_reference_value())
                    for _ in range(65 - current_references_count)
                ]
                UniqueReference.objects.bulk_create(new_references)

        except Exception as e:
            logger.error(f"Error in ensure_user_has_65_unique_references: {e}", exc_info=True)

@receiver(post_save, sender=RecyclerPricing)
def update_broken_screen_price(sender, instance, **kwargs):
    # Mettez à jour le prix pour tous les écrans cassés liés à cette offre et ce recycler
    BrokenScreen.objects.filter(quotations=instance, recycler=instance.recycler, is_packed=False).update(price=instance.price)

@receiver(pre_save, sender=ScreenModel)
def pre_save_screenmodel(sender, instance, **kwargs):
    # Vérifiez si is_wanted est en train de passer de True à False
    if instance.pk:
        old_instance = ScreenModel.objects.get(pk=instance.pk)
        if old_instance.is_wanted and not instance.is_wanted:
            # Obtenez tous les RecyclerPricing à supprimer
            recycler_pricings_to_delete = RecyclerPricing.objects.filter(
                screenmodel=instance,
                recycler__is_us=True,
                broken_screens__screenmodel=instance
            )
            # Supprimez-les
            recycler_pricings_to_delete.delete()