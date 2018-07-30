# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from feed.models import Channel
from feed.utils import get_feed
from datetime import datetime

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    既存チャンネルの更新をする
    Cronから定期的に呼ばれることを想定
    """
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
        既存チャンネル新着エピソードを取得
        """
        verbose = options['verbose']
        channels = Channel.objects.all()
        num_channels = len(channels)
        start = datetime.now()
        exec_time = start.strftime('%Y/%m/%d %H:%M:%S')

        if verbose:
            print('##########################################################################')
            print('[%s] %d channels to process..' % (
                exec_time, num_channels))

        for i, channel in enumerate(channels):
            if verbose:
                print('(%d/%d) Processing Channels' % (
                    i + 1, num_channels))
            # feed取得
            get_feed(channel.feed_url)

        end = datetime.now()
        end_time = end.strftime('%Y/%m/%d %H:%M:%S')
        print('[%s] logue get_feeds completed successfully' % (
            end_time))
        logger.info('[%s] logue get_feeds completed successfully' % (
            end_time))
