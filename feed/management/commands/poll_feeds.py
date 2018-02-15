from django.core.management.base import BaseCommand
from feed.models import Channel
from feed.utils import poll_feed

import logging

logger = logging.getLogger('logue monkey')


class Command(BaseCommand):
    help = '新着エピソードを取得'

    def add_arguments(self, parser):
        """
        省略可能な引数
        """
        parser.add_argument('--verbose',
                            action='store_true',
                            dest='verbose',
                            default=False,
                            help='Print progress on command line')

    def handle(self, *args, **options):
        """
        既存チャンネルの新着エピソードを取得
        """
        verbose = options['verbose']
        channels = Channel.objects.all()
        num_channels = len(channels)

        if verbose:
            print('%d channels to process' % (num_channels))

        for i, channel in enumerate(channels):
            if verbose:
                print('(%d/%d) Processing Channels' % (
                    i + 1, num_channels))

            poll_feed(channel)
        logger.info('logue monkey poll_feeds completed successfully')
