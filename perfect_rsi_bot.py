#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بوت RSI المثالي - نسخة محسنة بالكامل
تنبيهات فورية + تحديثات كل 30 دقيقة
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as ta
import requests
from telegram import Bot
from telegram.error import TelegramError

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)


class PerfectRSIBot:
    """بوت RSI المثالي مع جميع المميزات المطلوبة"""
    
    def __init__(self, telegram_token: str, telegram_chat_id: str):
        self.bot = Bot(token=telegram_token)
        self.telegram_chat_id = telegram_chat_id
        self.base_url = "https://api.bybit.com"
        
        # إعدادات RSI
        self.rsi_alert_threshold = 85  # حد التنبيه الفوري (85 أو أعلى فقط)
        self.rsi_period = 14
        
        # إعدادات التنبيهات
        self.alert_cooldown = {}  # تتبع آخر تنبيه لكل عملة
        self.last_alert_level = {}  # تتبع مستوى آخر تنبيه لكل عملة
        self.cooldown_hours = 4  # فترة انتظار بين التنبيهات
        
        # إعدادات التحديثات
        self.scan_count = 0
        self.total_alerts_sent = 0
        self.last_status_time = datetime.now()
        self.status_interval_minutes = 30  # تحديث كل 30 دقيقة كما طلبت
        
        # إحصائيات
        self.stats = {
            'total_scans': 0,
            'total_alerts': 0,
            'alerts_sent': 0,
            'last_alert_symbol': None,
            'last_alert_rsi': None
        }
    
    def get_usdt_perpetual_symbols(self):
        """جلب جميع عملات USDT Perpetual من Bybit"""
        try:
            endpoint = f"{self.base_url}/v5/market/instruments-info"
            params = {
                "category": "linear",
                "limit": 1000
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            data = response.json()
            
            if data.get("retCode") == 0:
                symbols = []
                for item in data["result"]["list"]:
                    if item.get("contractType") == "LinearPerpetual" and item["symbol"].endswith("USDT"):
                        symbols.append(item["symbol"])
                
                logger.info(f"✅ تم العثور على {len(symbols)} عملة USDT Perpetual")
                return symbols
            else:
                logger.error(f"❌ خطأ في API: {data.get('retMsg')}")
                return []
                
        except Exception as e:
            logger.error(f"❌ خطأ في جلب العملات: {e}")
            return []
    
    def get_kline_data(self, symbol: str, interval: str = "240", limit: int = 100):
        """جلب بيانات الشموع لعملة معينة (4 ساعات)"""
        try:
            endpoint = f"{self.base_url}/v5/market/kline"
            params = {
                "category": "linear",
                "symbol": symbol,
                "interval": interval,  # 240 = 4 ساعات
                "limit": limit
            }
            
            response = requests.get(endpoint, params=params, timeout=5)
            data = response.json()
            
            if data.get("retCode") == 0 and data["result"]["list"]:
                klines = data["result"]["list"]
                df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
                df['close'] = pd.to_numeric(df['close'])
                df = df.sort_values('timestamp')
                return df
            
            return None
            
        except Exception as e:
            logger.debug(f"خطأ في جلب بيانات {symbol}: {e}")
            return None
    
    def calculate_rsi(self, df: pd.DataFrame):
        """حساب مؤشر RSI"""
        try:
            if df is None or len(df) < self.rsi_period + 1:
                return None
            
            rsi = ta.rsi(df['close'], length=self.rsi_period)
            
            if rsi is not None and len(rsi) > 0:
                return float(rsi.iloc[-1])
            
            return None
            
        except Exception as e:
            logger.debug(f"خطأ في حساب RSI: {e}")
            return None
    
    async def send_immediate_alert(self, symbol: str, rsi_value: float):
        """إرسال تنبيه فوري للتيليجرام عند RSI >= 85 فقط"""
        try:
            current_time = datetime.now()
            
            # تحديد مستوى التنبيه الحالي
            current_level = "very_high" if rsi_value >= 90 else "high"
            
            # التحقق من cooldown مع استثناء لـ RSI 90
            if symbol in self.alert_cooldown:
                time_diff = (current_time - self.alert_cooldown[symbol]).total_seconds() / 3600
                if time_diff < self.cooldown_hours:
                    # السماح بتنبيه RSI 90 حتى لو في فترة انتظار
                    last_level = self.last_alert_level.get(symbol, "")
                    if current_level == "very_high" and last_level != "very_high":
                        logger.info(f"إرسال تنبيه RSI 90 لـ {symbol} - تجاوز فترة الانتظار")
                    else:
                        logger.info(f"تجاهل التنبيه لـ {symbol} - في فترة الانتظار")
                        return False
            
            # تحديد مستوى التنبيه
            if rsi_value >= 90:
                emoji = "🚨🚨🚨"
                level = "عالي جداً"
                color = "🔴"
                action = "⚠️ انتبه! RSI مرتفع جداً - فرصة قوية للبيع"
            else:  # 85-89
                emoji = "⚠️⚠️"
                level = "عالي"
                color = "🟡"
                action = "💡 RSI مرتفع - راقب العملة للبيع"
            
            self.stats['alerts_sent'] += 1
            self.stats['last_alert_symbol'] = symbol
            self.stats['last_alert_rsi'] = rsi_value
            
            alert_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"""{emoji} **تنبيه RSI {level}!** {emoji}

{color} **مستوى التنبيه:** RSI {level}
💎 **العملة:** {symbol}
📊 **قيمة RSI:** {rsi_value:.2f}
⏰ **الوقت:** {alert_time}
📈 **الإطار الزمني:** 4 ساعات

{action}

━━━━━━━━━━━━━━━━━━━━━
🔔 لن تتلقى تنبيه آخر لهذه العملة لمدة {self.cooldown_hours} ساعات
📱 التنبيهات فقط عند RSI ≥ 85"""
            
            await self.bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
            # تحديث cooldown والإحصائيات ومستوى التنبيه
            self.alert_cooldown[symbol] = current_time
            self.last_alert_level[symbol] = current_level
            self.total_alerts_sent += 1
            self.stats['total_alerts'] += 1
            
            logger.info(f"✅ تم إرسال تنبيه {level} لـ {symbol} - RSI: {rsi_value:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال التنبيه: {e}")
            return False
    
    async def send_periodic_status(self, symbols_checked, very_high_rsi, high_rsi, moderate_rsi, low_rsi):
        """إرسال تحديث دوري كل 30 دقيقة عن حالة السوق"""
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # إعداد قوائم العملات
            very_high_list = ""
            if very_high_rsi:
                very_high_list = "\n".join([f"  • {s}: {r:.2f}" for s, r in very_high_rsi[:5]])
            else:
                very_high_list = "  • لا توجد عملات"
            
            high_list = ""
            if high_rsi:
                high_list = "\n".join([f"  • {s}: {r:.2f}" for s, r in high_rsi[:5]])
            else:
                high_list = "  • لا توجد عملات"
            
            moderate_list = ""
            if moderate_rsi:
                moderate_list = "\n".join([f"  • {s}: {r:.2f}" for s, r in moderate_rsi[:3]])
            
            # حساب النسب المئوية
            total = len(very_high_rsi) + len(high_rsi) + len(moderate_rsi) + len(low_rsi)
            very_high_percent = (len(very_high_rsi) / total * 100) if total > 0 else 0
            high_percent = (len(high_rsi) / total * 100) if total > 0 else 0
            
            message = f"""📊 **تحديث السوق الدوري - كل 30 دقيقة**

⏰ **الوقت:** {current_time}
🔍 **الفحص رقم:** #{self.scan_count}
✅ **العملات المفحوصة:** {symbols_checked}

━━━━━━━━━━━━━━━━━━━━━
🔴 **RSI عالي جداً (≥90):** {len(very_high_rsi)} عملة ({very_high_percent:.1f}%)
{very_high_list}

🟡 **RSI عالي (70-89):** {len(high_rsi)} عملة ({high_percent:.1f}%)
{high_list}

🟠 **RSI متوسط (50-69):** {len(moderate_rsi)} عملة
{moderate_list if moderate_rsi else '  • لا توجد عملات'}

🟢 **RSI منخفض (<50):** {len(low_rsi)} عملة

━━━━━━━━━━━━━━━━━━━━━
📈 **إحصائيات اليوم:**
  • إجمالي التنبيهات المرسلة: {self.stats['alerts_sent']}
  • عدد الفحوصات: {self.scan_count}

🎯 **آخر تنبيه:**
  • العملة: {self.stats['last_alert_symbol'] or 'لا يوجد'}
  • RSI: {self.stats['last_alert_rsi']:.2f if self.stats['last_alert_rsi'] else 'لا يوجد'}

━━━━━━━━━━━━━━━━━━━━━
✅ البوت يعمل بشكل ممتاز
🔔 تنبيهات فورية فقط عند RSI ≥ 85
📱 التحديث القادم بعد 30 دقيقة"""
            
            await self.bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info("✅ تم إرسال التحديث الدوري")
            
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال التحديث الدوري: {e}")
    
    async def scan_all_symbols(self):
        """فحص جميع العملات وإرسال التنبيهات الفورية"""
        self.scan_count += 1
        self.stats['total_scans'] += 1
        logger.info(f"🔍 بدء الفحص #{self.scan_count}")
        
        symbols = self.get_usdt_perpetual_symbols()
        if not symbols:
            logger.warning("⚠️ لم يتم العثور على عملات")
            return
        
        # تصنيف العملات حسب RSI
        very_high_rsi = []  # RSI >= 90
        high_rsi = []       # RSI 70-89
        moderate_rsi = []   # RSI 50-69
        low_rsi = []        # RSI < 50
        symbols_checked = 0
        
        # فحص كل عملة
        for i, symbol in enumerate(symbols):
            try:
                df = self.get_kline_data(symbol)
                if df is None:
                    continue
                
                rsi_value = self.calculate_rsi(df)
                if rsi_value is None:
                    continue
                
                symbols_checked += 1
                
                # التحقق من التنبيهات الفورية (فقط عند RSI >= 85)
                if rsi_value >= self.rsi_alert_threshold:
                    await self.send_immediate_alert(symbol, rsi_value)
                
                # تصنيف للتقرير الدوري
                if rsi_value >= 90:
                    very_high_rsi.append((symbol, rsi_value))
                elif rsi_value >= 70:
                    high_rsi.append((symbol, rsi_value))
                elif rsi_value >= 50:
                    moderate_rsi.append((symbol, rsi_value))
                else:
                    low_rsi.append((symbol, rsi_value))
                
                # تحديث التقدم كل 50 عملة
                if (i + 1) % 50 == 0:
                    logger.info(f"📈 التقدم: {i+1}/{len(symbols)} عملة")
                
                # تأخير صغير لتجنب حدود API
                await asyncio.sleep(0.3)
                
            except Exception as e:
                logger.error(f"خطأ في فحص {symbol}: {e}")
                continue
        
        # ترتيب القوائم حسب RSI (الأعلى أولاً)
        very_high_rsi.sort(key=lambda x: x[1], reverse=True)
        high_rsi.sort(key=lambda x: x[1], reverse=True)
        moderate_rsi.sort(key=lambda x: x[1], reverse=True)
        low_rsi.sort(key=lambda x: x[1], reverse=True)
        
        # سجل الملخص
        logger.info(f"""
✅ انتهى الفحص #{self.scan_count}:
  - العملات المفحوصة: {symbols_checked}/{len(symbols)}
  - RSI عالي جداً (≥90): {len(very_high_rsi)}
  - RSI عالي (70-89): {len(high_rsi)}
  - RSI متوسط (50-69): {len(moderate_rsi)}
  - RSI منخفض (<50): {len(low_rsi)}
  - التنبيهات المرسلة هذا الفحص: {self.total_alerts_sent}
        """)
        
        # إرسال تحديث دوري كل 30 دقيقة فقط
        current_time = datetime.now()
        time_diff = (current_time - self.last_status_time).total_seconds() / 60
        
        if time_diff >= self.status_interval_minutes:
            await self.send_periodic_status(
                symbols_checked,
                very_high_rsi,
                high_rsi,
                moderate_rsi,
                low_rsi
            )
            self.last_status_time = current_time
    
    async def run(self, check_interval: int = 60):
        """تشغيل البوت - فحص كل دقيقة"""
        logger.info(f"🚀 بدء تشغيل البوت - فحص كل {check_interval} ثانية")
        
        # رسالة البداية
        try:
            startup_msg = f"""🚀 **بوت مراقبة RSI يعمل الآن!** 🚀

⚙️ **الإعدادات:**
  • 📊 فحص كل {check_interval} ثانية
  • 🎯 تنبيهات فورية فقط عند RSI ≥ 85
  • 📈 تقارير دورية كل 30 دقيقة
  • ⏰ فترة الانتظار: {self.cooldown_hours} ساعات
  • 💹 عدد العملات: يتم فحص جميع عملات USDT Perpetual

🔔 **التنبيهات الفورية:**
  • 🔴 تنبيه فوري عند RSI ≥ 85 فقط
  • 📊 تقرير شامل كل 30 دقيقة

✅ البوت جاهز ويراقب السوق
📱 ستتلقى تنبيهات فقط للفرص القوية (RSI ≥ 85)

━━━━━━━━━━━━━━━━━━━━━
• لا تكرار للتنبيهات لـ 4 ساعات
• تنبيهات فورية لكل عملة
• رسائل واضحة بالعربية
• إحصائيات مفصلة

━━━━━━━━━━━━━━━━━━━━━
🔍 جاري فحص السوق الآن...
📱 ستتلقى التنبيهات الفورية + تحديث كل 30 دقيقة"""
            
            await self.bot.send_message(
                chat_id=self.telegram_chat_id,
                text=startup_msg,
                parse_mode='Markdown'
            )
            logger.info("✅ تم إرسال رسالة البداية")
            
        except Exception as e:
            logger.error(f"❌ خطأ في إرسال رسالة البداية: {e}")
        
        # الحلقة الرئيسية
        while True:
            try:
                await self.scan_all_symbols()
                logger.info(f"⏳ انتظار {check_interval} ثانية للفحص التالي...")
                await asyncio.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 توقف البوت بواسطة المستخدم")
                break
            except Exception as e:
                logger.error(f"❌ خطأ في الحلقة الرئيسية: {e}")
                await asyncio.sleep(check_interval)


async def main():
    """الدالة الرئيسية"""
    print("=" * 60)
    print("Perfect RSI Bot - Full Arabic Version")
    print("=" * 60)
    
    # تحميل الإعدادات
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    telegram_token = config.get('telegram_bot_token')
    telegram_chat_id = config.get('telegram_chat_id')
    check_interval = config.get('check_interval', 60)
    
    print(f"\nBot Configuration:")
    print(f"  - Chat ID: {telegram_chat_id}")
    print(f"  - Check Interval: {check_interval} seconds")
    print(f"  - High RSI Alert: >= 70")
    print(f"  - Very High RSI Alert: >= 90")
    print(f"  - Status Updates: Every 30 minutes")
    
    print("\n[INFO] Starting Perfect RSI Bot...")
    print("[INFO] Immediate alerts + 30-min status updates")
    print("[INFO] Press Ctrl+C to stop\n")
    print("=" * 60 + "\n")
    
    # إنشاء وتشغيل البوت
    bot = PerfectRSIBot(telegram_token, str(telegram_chat_id))
    
    # يمكن تخصيص الإعدادات من config.json
    bot.rsi_very_high = config.get('rsi_very_high', 90)
    bot.rsi_high = config.get('rsi_high', 70)
    bot.rsi_period = config.get('rsi_period', 14)
    bot.cooldown_hours = config.get('alert_cooldown_hours', 4)
    bot.status_interval_minutes = 30  # ثابت كما طلبت
    
    await bot.run(check_interval)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[INFO] Bot stopped successfully")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
