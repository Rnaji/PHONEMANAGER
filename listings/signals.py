# dans votre_app/signals.py

from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from .models import UniqueReference, RepairStore, RecyclerPricing, BrokenScreen, ScreenModel, Recycler
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
            # Obtenez tous les Recycler avec is_us=True
            recyclers_with_us = Recycler.objects.filter(is_us=True)
            
            # Parcourez chaque Recycler avec is_us=True
            for recycler_with_us in recyclers_with_us:
                # Obtenez tous les BrokenScreen liés à cet ScreenModel et Recycler
                broken_screens = BrokenScreen.objects.filter(
                    screenmodel=instance,
                    recycler=recycler_with_us
                )
                # Parcourez chaque BrokenScreen et supprimez le champ recycler
                for broken_screen in broken_screens:
                    broken_screen.recycler = None
                    broken_screen.save()

# signals.py
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ScreenModel, BrokenScreen

logger = logging.getLogger(__name__)

# signals.py
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ScreenModel, BrokenScreen

logger = logging.getLogger(__name__)


# signals.py
@receiver(post_save, sender=ScreenModel)
def handle_screenmodel_change(sender, instance, **kwargs):
    logger.info("Signal handle_screenmodel_change triggered!")

    if 'update_fields' in kwargs and kwargs['update_fields'] is not None and 'is_wanted' in kwargs['update_fields']:
        screenmodel = instance
        logger.info(f"ScreenModel {screenmodel} is_wanted changed to {screenmodel.is_wanted}")

        if screenmodel:
            broken_screens = BrokenScreen.objects.filter(screenmodel=screenmodel, grade='A')
            logger.info(f"Found {broken_screens.count()} BrokenScreens with ScreenModel {screenmodel} and grade 'A'")

            for broken_screen in broken_screens:
                logger.info(f"Processing BrokenScreen with ID {broken_screen.id}")

                # Récupérez uniquereference pour le BrokenScreen actuel
                uniquereference = broken_screen.uniquereference  # Assurez-vous que c'est la bonne relation

                # Vérifiez que uniquereference n'est pas None avant de continuer
                if uniquereference:
                    logger.info(f"Processing UniqueReference with ID {uniquereference.id}")

                    # Effectuez ici les actions nécessaires pour rafraîchir les données pour ces instances
                    broken_screen.quotations.clear()
                    # Effectuez ici les actions nécessaires pour mettre à jour les quotations selon vos besoins
                    # Exemple: broken_screen.quotations.add(new_quotation_instance)

                    broken_screen.save()

                    # Rafraîchissez les quotations via l'URL
                    # NOTE: Vous devrez adapter cette partie en fonction de votre logique d'URL et de vue
                    quotation_url = f"quotation/{uniquereference.id}"  # Assurez-vous que c'est la bonne logique d'URL
                    # Effectuez ici les actions nécessaires pour rafraîchir les quotations via l'URL
                    # Exemple: requests.get(quotation_url)

                    logger.info(f"Processed UniqueReference with ID {uniquereference.id}")

                logger.info(f"Processed BrokenScreen with ID {broken_screen.id}")

    logger.info("Signal handle_screenmodel_change complete!")



