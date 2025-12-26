"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: monetize_bot.py                                                       ║
║  Generated: 2025-12-26T10:00:42.199916                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ==============================================================================
# PRIMSX CODEX - MONETIZE_BOT.PY
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

import discord, stripe, os
       from discord.ext import commands
       from dotenv import load_dotenv
       load_dotenv('/home/boozelee/Desktop/superbrain-x/api-keys/discord.env')
       stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
       bot = commands.Bot(command_prefix='!')

       @bot.command()
       async def subscribe(ctx, tier='basic'):
           prices = {'basic': 'price_basic', 'pro': 'price_pro'}
           session = stripe.checkout.Session.create(
               payment_method_types=['card'],
               line_items=[{'price': prices[tier], 'quantity': 1}],
               mode='subscription',
               success_url='https://superbrain.ai/success',
               cancel_url='https://superbrain.ai/cancel'
           )
           await ctx.send(f'Subscribe: {session.url}')
       bot.run(os.getenv('DISCORD_BOT_TOKEN'))