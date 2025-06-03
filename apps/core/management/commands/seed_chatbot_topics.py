from django.core.management.base import BaseCommand
from apps.core.models import ChatbotTopic


class Command(BaseCommand):
    help = 'Seed initial chatbot topics for massage therapy'

    def handle(self, *args, **kwargs):
        topics = [
            # English topics
            {
                'label': 'What are the benefits?',
                'question': 'What are the main benefits of massage therapy?',
                'language': 'en',
                'order': 1
            },
            {
                'label': 'Contraindications',
                'question': 'Are there any contraindications for massage therapy?',
                'language': 'en',
                'order': 2
            },
            {
                'label': 'Types of massage',
                'question': 'What types of massage do you offer?',
                'language': 'en',
                'order': 3
            },
            {
                'label': 'How to prepare?',
                'question': 'How should I prepare for my massage appointment?',
                'language': 'en',
                'order': 4
            },
            {
                'label': 'Aftercare tips',
                'question': 'What should I do after my massage session?',
                'language': 'en',
                'order': 5
            },
            
            # Romanian topics
            {
                'label': 'Cât durează o ședință?',
                'question': 'Cât durează o ședință de masaj terapeutic?',
                'language': 'ro',
                'order': 1
            },
            {
                'label': 'Beneficii masaj',
                'question': 'Care sunt beneficiile masajului terapeutic?',
                'language': 'ro',
                'order': 2
            },
            {
                'label': 'Tipuri de masaj',
                'question': 'Ce tipuri de masaj oferiți?',
                'language': 'ro',
                'order': 3
            },
            {
                'label': 'Cum să mă pregătesc',
                'question': 'Cum ar trebui să mă pregătesc pentru ședința de masaj?',
                'language': 'ro',
                'order': 4
            },
            {
                'label': 'Sfaturi după masaj',
                'question': 'Ce ar trebui să fac după ședința de masaj?',
                'language': 'ro',
                'order': 5
            },
            
            # German topics
            {
                'label': 'Kontraindikationen',
                'question': 'Gibt es Kontraindikationen für Massagetherapie?',
                'language': 'de',
                'order': 1
            },
            {
                'label': 'Massagearten',
                'question': 'Welche Arten von Massagen bieten Sie an?',
                'language': 'de',
                'order': 2
            },
            {
                'label': 'Vorbereitung',
                'question': 'Wie sollte ich mich auf meine Massage vorbereiten?',
                'language': 'de',
                'order': 3
            },
            {
                'label': 'Nachbehandlung',
                'question': 'Was sollte ich nach meiner Massage beachten?',
                'language': 'de',
                'order': 4
            },
            {
                'label': 'Vorteile',
                'question': 'Welche Vorteile bietet die Massagetherapie?',
                'language': 'de',
                'order': 5
            }
        ]

        created_count = 0
        for topic in topics:
            obj, created = ChatbotTopic.objects.get_or_create(
                label=topic['label'],
                language=topic['language'],
                defaults={
                    'question': topic['question'],
                    'order': topic['order'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created topic: {topic["label"]} ({topic["language"]})'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} new chatbot topics!'
            )
        ) 