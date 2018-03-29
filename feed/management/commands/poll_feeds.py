# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from feed.models import Channel
from feed.utils import poll_feed
from datetime import datetime

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
        start = datetime.now()
        exec_time = start.strftime('%Y/%m/%d %H:%M:%S')

        if verbose:
            print('##################################################')
            print('%d channels to process.. started at %s' % (
                num_channels, exec_time))

        for i, channel in enumerate(channels):
            if verbose:
                print('(%d/%d) Processing Channels' % (
                    i + 1, num_channels))
            # feed取得
            poll_feed(channel)

        end = datetime.now()
        end_time = end.strftime('%Y/%m/%d %H:%M:%S')
        print('logue poll_feeds completed successfully at %s' % (
            end_time))
        logger.info('logue poll_feeds completed successfully at %s' % (
            end_time))
