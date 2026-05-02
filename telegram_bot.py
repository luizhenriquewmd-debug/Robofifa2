import os
from telegram import Bot
from telegram.error import TelegramError
from config import Config
from utils import Logger
import asyncio
from datetime import datetime

class TelegramBotManager:
    """Gerencia comunicação com Telegram"""
    
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.logger = Logger()
        
        if not self.bot_token or not self.chat_id:
            self.logger.error("Token ou Chat ID não configurados")
            raise ValueError("TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID devem estar configurados")
        
        self.bot = Bot(token=self.bot_token)
        self.message_history = []
    
    def send_alert(self, match_data, opportunity, odd=None):
        """Envia alerta para Telegram"""
        try:
            message = self._format_alert_message(match_data, opportunity, odd)
            
            # Envia mensagem
            asyncio.run(self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            ))
            
            # Registra no histórico
            self.message_history.append({
                'timestamp': datetime.now(),
                'match_id': match_data['match_id'],
                'type': opportunity['type'],
                'message': message
            })
            
            self.logger.info(f"Alerta enviado: {opportunity['type']} - {match_data['match_id']}")
            return True
            
        except TelegramError as e:
            self.logger.error(f"Erro ao enviar mensagem Telegram: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado ao enviar alerta: {e}")
            return False
    
    def send_status_update(self, status_message):
        """Envia atualização de status do bot"""
        try:
            asyncio.run(self.bot.send_message(
                chat_id=self.chat_id,
                text=status_message,
                parse_mode='Markdown'
            ))
            self.logger.info("Status enviado")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao enviar status: {e}")
            return False
    
    def _format_alert_message(self, match_data, opportunity, odd=None):
        """Formata mensagem de alerta"""
        
        home = match_data['player_home']
        away = match_data['player_away']
        minute = match_data.get('current_minute', 0)
        score_home = match_data['score_home']
        score_away = match_data['score_away']
        
        # Header
        message = f"🔥 *OPORTUNIDADE DETECTADA*\n\n"
        
        # Match info
        message += f"⚽ *{home}* vs *{away}*\n"
        message += f"⏱️ Tempo: {minute}'\n"
        message += f"📊 Placar: `{{score_home}} x {{score_away}}`\n"
        message += f"📈 Total: {{score_home + score_away}} gols\n\n"
        
        # Opportunity
        message += f"🎯 *{{opportunity['suggestion']}}*\n"
        if odd:
            message += f"💰 Odd: `{{odd:.2f}}`\n"
        message += f"📍 Confiança: `{{opportunity['confidence']}}%`\n\n"
        
        # Analysis
        message += f"📋 *Análise:*\n"
        message += f"_{{opportunity['reasoning']}}_\n\n"
        
        # Tips
        message += f"⚠️ *Dicas:*\n"
        message += f"• Sempre valide a odd no seu app\n"
        message += f"• Nunca aposta mais que 5% do bankroll\n"
        message += f"• Este sistema não garante lucro\n\n"
        
        # Footer
        message += f"🤖 Bot v1.0 | {{datetime.now().strftime('%H:%M:%S')}}"
        
        return message
    
    def send_startup_message(self):
        """Envia mensagem de inicialização"""
        message = '''
🤖 *FIFA BATTLE BOT INICIADO*

✅ Bot rodando e monitorando partidas E-Soccer Battle

📊 Funcionalidades:
• Análise em tempo real de partidas
• Detecção de padrões estatísticos
• Alertas com confiança > 70%
• Gerenciamento de risco

⚠️ Lembretes importantes:
• Este bot não garante lucro
• Baseado em análise estatística apenas
• Use com responsabilidade

🎯 Monitorando jogadores...
'''        
        self.send_status_update(message)
    
    def send_shutdown_message(self):
        """Envia mensagem de encerramento"""
        message = '''
🛑 *FIFA BATTLE BOT ENCERRADO*

❌ Bot parou de monitorar

📊 Estatísticas da sessão podem ser consultadas em `bot.log`
'''        
        self.send_status_update(message)
    
    def send_test_message(self):
        """Envia mensagem de teste"""
        try:
            asyncio.run(self.bot.send_message(
                chat_id=self.chat_id,
                text="✅ Conexão Telegram OK! Bot está funcionando.",
                parse_mode='Markdown'
            ))
            self.logger.info("Mensagem de teste enviada com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem de teste: {e}")
            return False


class AlertFormatter:
    """Formata diferentes tipos de alertas"""    
    @staticmethod
    def format_early_goal_alert(match_data, confidence):
        """Formata alerta de gol cedo"""        
        return f'''
🚀 *GOL CEDO*

{{match_data['player_home']}} vs {{match_data['player_away']}}
Minuto: {{match_data.get('current_minute', 0)}}'

Ambos times têm histórico de gols cedo!
Confiança: {{confidence}}%
        '''.strip()    
    @staticmethod
    def format_over_ht_alert(match_data, confidence):
        """Formata alerta de over no intervalo"""        
        return f'''
🏟️ *OVER 2.5 INTERVALO*

{{match_data['player_home']}} vs {{match_data['player_away']}}
Placar: {{match_data['score_home']}}x{{match_data['score_away']}}

Jogo aberto! Propensão a over no 1º tempo.
Confiança: {{confidence}}%
        '''.strip()    
    @staticmethod
    def format_over_ft_alert(match_data, confidence):
        """Formata alerta de over no final"""        
        return f'''
⚽ *OVER 4.5 / 5.5 FINAL*

{{match_data['player_home']}} vs {{match_data['player_away']}}
Placar: {{match_data['score_home']}}x{{match_data['score_away']}}

Ritmo alto mantido! Tendência forte de over.
Confiança: {{confidence}}%
        '''.strip()