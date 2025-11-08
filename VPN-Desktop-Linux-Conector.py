#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango
import subprocess
import threading
import signal
import json
import os
import base64
import socket

# Intentar importar requests (opcional)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Advertencia: módulo 'requests' no está disponible. No se podrá obtener la IP pública.")
    print("Para instalarlo: pip3 install requests")

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# Diccionario de traducciones
TRADUCCIONES = {
    'es': {
        'title': 'Conectar VPN - OpenVPN',
        'menu_config': 'Configuración',
        'menu_themes': 'Temas',
        'theme_managerial': 'Gerencial',
        'theme_minimalist': 'Minimalista',
        'theme_modern': 'Moderno',
        'theme_solar': 'Sistema Solar',
        'menu_language': 'Lenguaje',
        'force_tls': 'Forzar TLS 1.0/AES-128-CBC',
        'anti_suspend': 'Modo anti-suspensión (30s)',
        'show_console_log': 'Mostrar log de consola',
        'notification_connected': 'Conectado a la VPN',
        'yes': 'Sí',
        'no': 'No',
        'tls_error_title': 'Error de TLS Deprecado',
        'tls_error_msg': 'Se detectó un error de TLS deprecado.\n\n¿Desea activar el uso de TLS 1.0 con Cifrado AES-128-CBC?\n\nEsto puede resolver problemas de compatibilidad con servidores antiguos.',
        'menu_help': 'Ayuda',
        'help_manual': 'Manual de VPN Linux Desktop Connector',
        'help_report_bug': 'Informar de fallo',
        'help_donate': 'Hacer un donativo',
        'help_about': 'Acerca de VPN Linux Desktop Connector',
        'lang_spanish': 'Español',
        'lang_chinese': 'Chino',
        'lang_portuguese': 'Portugués',
        'lang_french': 'Francés',
        'lang_german': 'Alemán',
        'lang_english': 'Inglés',
        'lang_japanese': 'Japonés',
        'lang_native_es': 'Español',
        'lang_native_zh': '中文',
        'lang_native_pt': 'Português',
        'lang_native_fr': 'Français',
        'lang_native_de': 'Deutsch',
        'lang_native_en': 'English',
        'lang_native_ja': '日本語',
        'label_user': 'Usuario:',
        'label_password': 'Contraseña:',
        'label_ovpn': 'Archivo OVPN:',
        'placeholder_user': 'Ingrese usuario',
        'placeholder_password': 'Ingrese contraseña',
        'btn_select_ovpn': 'Seleccionar archivo OVPN',
        'btn_connect': 'Conectar VPN',
        'btn_disconnect': 'Desconectar VPN',
        'btn_connecting': 'Conectando VPN',
        'btn_disconnecting': 'Desconectando VPN',
        'btn_clear': 'Limpiar Logs',
        'status': 'Estado:',
        'status_disconnected': 'Desconectado',
        'status_connecting': 'Conectando...',
        'status_connected': 'Conectado ✓',
        'status_disconnecting': 'Desconectando...',
        'initial_msg': "Presiona 'Conectar VPN' para iniciar la conexión.\n",
        'dialog_select_ovpn': 'Seleccionar archivo OVPN',
        'filter_ovpn': 'Archivos OVPN',
        'filter_all': 'Todos los archivos',
        'file_selected': 'Archivo OVPN seleccionado:',
        'error_required': 'Campos requeridos',
        'error_required_msg': 'Por favor ingrese usuario y contraseña.',
        'error_ovpn_required': 'Archivo OVPN requerido',
        'error_ovpn_required_msg': 'Por favor seleccione un archivo OVPN.',
        'starting_connection': '=== Iniciando conexión VPN ===\n',
        'user': 'Usuario:',
        'credentials_saved': 'Credenciales guardadas en config.txt\n\n',
        'disconnecting_vpn': '\n=== Desconectando VPN (Ctrl+C) ===\n',
        'vpn_disconnected': '\n=== VPN Desconectada ===\n',
        'connection_error': '\n=== Error al conectar ===\n',
        'vpn_disconnected_ok': '\n=== VPN desconectada correctamente ===\n',
        'vpn_disconnected_error': '\n=== VPN desconectada (con errores) ===\n',
        'process_ended': '\n=== Proceso terminado con código',
        'error': 'Error:',
        'error_connection_title': 'Error de conexión',
        'error_connection_msg': 'No se puede conectar con los parámetros seleccionados.\n\nVerifique:\n- Usuario y contraseña correctos\n- Archivo OVPN válido\n- Conexión a internet',
    },
    'en': {
        'title': 'VPN Connect - OpenVPN',
        'menu_config': 'Settings',
        'menu_themes': 'Themes',
        'theme_managerial': 'Managerial',
        'theme_minimalist': 'Minimalist',
        'theme_modern': 'Modern',
        'theme_solar': 'Solar System',
        'menu_language': 'Language',
        'force_tls': 'Force TLS 1.0/AES-128-CBC',
        'anti_suspend': 'Anti-suspend mode (30s)',
        'show_console_log': 'Show console log',
        'notification_connected': 'Connected to VPN',
        'yes': 'Yes',
        'no': 'No',
        'tls_error_title': 'Deprecated TLS Error',
        'tls_error_msg': 'A deprecated TLS error was detected.\n\nDo you want to enable TLS 1.0 with AES-128-CBC Encryption?\n\nThis may resolve compatibility issues with older servers.',
        'menu_help': 'Help',
        'help_manual': 'VPN Linux Desktop Connector Manual',
        'help_report_bug': 'Report a Bug',
        'help_donate': 'Make a Donation',
        'help_about': 'About VPN Linux Desktop Connector',
        'lang_spanish': 'Spanish',
        'lang_chinese': 'Chinese',
        'lang_portuguese': 'Portuguese',
        'lang_french': 'French',
        'lang_german': 'German',
        'lang_english': 'English',
        'lang_japanese': 'Japanese',
        'lang_native_es': 'Español',
        'lang_native_zh': '中文',
        'lang_native_pt': 'Português',
        'lang_native_fr': 'Français',
        'lang_native_de': 'Deutsch',
        'lang_native_en': 'English',
        'lang_native_ja': '日本語',
        'label_user': 'Username:',
        'label_password': 'Password:',
        'label_ovpn': 'OVPN File:',
        'placeholder_user': 'Enter username',
        'placeholder_password': 'Enter password',
        'btn_select_ovpn': 'Select OVPN file',
        'btn_connect': 'Connect VPN',
        'btn_disconnect': 'Disconnect VPN',
        'btn_connecting': 'Connecting VPN',
        'btn_disconnecting': 'Disconnecting VPN',
        'btn_clear': 'Clear Logs',
        'status': 'Status:',
        'status_disconnected': 'Disconnected',
        'status_connecting': 'Connecting...',
        'status_connected': 'Connected ✓',
        'status_disconnecting': 'Disconnecting...',
        'initial_msg': "Press 'Connect VPN' to start the connection.\n",
        'dialog_select_ovpn': 'Select OVPN file',
        'filter_ovpn': 'OVPN Files',
        'filter_all': 'All files',
        'file_selected': 'OVPN file selected:',
        'error_required': 'Required fields',
        'error_required_msg': 'Please enter username and password.',
        'error_ovpn_required': 'OVPN file required',
        'error_ovpn_required_msg': 'Please select an OVPN file.',
        'starting_connection': '=== Starting VPN connection ===\n',
        'user': 'User:',
        'credentials_saved': 'Credentials saved in config.txt\n\n',
        'disconnecting_vpn': '\n=== Disconnecting VPN (Ctrl+C) ===\n',
        'vpn_disconnected': '\n=== VPN Disconnected ===\n',
        'connection_error': '\n=== Connection error ===\n',
        'vpn_disconnected_ok': '\n=== VPN disconnected successfully ===\n',
        'vpn_disconnected_error': '\n=== VPN disconnected (with errors) ===\n',
        'process_ended': '\n=== Process ended with code',
        'error': 'Error:',
        'error_connection_title': 'Connection error',
        'error_connection_msg': 'Cannot connect with selected parameters.\n\nCheck:\n- Correct username and password\n- Valid OVPN file\n- Internet connection',
    },
    'zh': {
        'title': 'VPN 连接 - OpenVPN',
        'menu_config': '配置',
        'menu_themes': '主题',
        'theme_managerial': '管理风格',
        'theme_minimalist': '极简主义',
        'theme_modern': '现代',
        'theme_solar': '太阳系',
        'menu_language': '语言',
        'force_tls': '强制 TLS 1.0/AES-128-CBC',
        'anti_suspend': '防休眠模式 (30秒)',
        'show_console_log': '显示控制台日志',
        'notification_connected': '已连接到VPN',
        'yes': '是',
        'no': '否',
        'tls_error_title': 'TLS 已弃用错误',
        'tls_error_msg': '检测到 TLS 已弃用错误。\n\n是否要启用 TLS 1.0 和 AES-128-CBC 加密？\n\n这可以解决与旧服务器的兼容性问题。',
        'menu_help': '帮助',
        'help_manual': 'VPN Linux Desktop Connector 手册',
        'help_report_bug': '报告错误',
        'help_donate': '捐赠',
        'help_about': '关于 VPN Linux Desktop Connector',
        'lang_spanish': '西班牙语',
        'lang_chinese': '中文',
        'lang_portuguese': '葡萄牙语',
        'lang_french': '法语',
        'lang_german': '德语',
        'lang_english': '英语',
        'lang_japanese': '日语',
        'lang_native_es': 'Español',
        'lang_native_zh': '中文',
        'lang_native_pt': 'Português',
        'lang_native_fr': 'Français',
        'lang_native_de': 'Deutsch',
        'lang_native_en': 'English',
        'lang_native_ja': '日本語',
        'label_user': '用户名：',
        'label_password': '密码：',
        'label_ovpn': 'OVPN 文件：',
        'placeholder_user': '输入用户名',
        'placeholder_password': '输入密码',
        'btn_select_ovpn': '选择 OVPN 文件',
        'btn_connect': '连接 VPN',
        'btn_disconnect': '断开 VPN',
        'btn_connecting': '正在连接 VPN',
        'btn_disconnecting': '正在断开 VPN',
        'btn_clear': '清除日志',
        'status': '状态：',
        'status_disconnected': '已断开',
        'status_connecting': '正在连接...',
        'status_connected': '已连接 ✓',
        'status_disconnecting': '正在断开...',
        'initial_msg': "按 '连接 VPN' 开始连接。\n",
        'dialog_select_ovpn': '选择 OVPN 文件',
        'filter_ovpn': 'OVPN 文件',
        'filter_all': '所有文件',
        'file_selected': '已选择 OVPN 文件：',
        'error_required': '必填字段',
        'error_required_msg': '请输入用户名和密码。',
        'error_ovpn_required': '需要 OVPN 文件',
        'error_ovpn_required_msg': '请选择 OVPN 文件。',
        'starting_connection': '=== 正在启动 VPN 连接 ===\n',
        'user': '用户：',
        'credentials_saved': '凭据已保存在 config.txt\n\n',
        'disconnecting_vpn': '\n=== 正在断开 VPN (Ctrl+C) ===\n',
        'vpn_disconnected': '\n=== VPN 已断开 ===\n',
        'connection_error': '\n=== 连接错误 ===\n',
        'vpn_disconnected_ok': '\n=== VPN 成功断开 ===\n',
        'vpn_disconnected_error': '\n=== VPN 断开（有错误）===\n',
        'process_ended': '\n=== 进程结束，代码',
        'error': '错误：',
        'error_connection_title': '连接错误',
        'error_connection_msg': '无法使用所选参数连接。\n\n请检查：\n- 用户名和密码正确\n- OVPN 文件有效\n- 互联网连接',
    },
    'pt': {
        'title': 'Conectar VPN - OpenVPN',
        'menu_config': 'Configuração',
        'menu_themes': 'Temas',
        'theme_managerial': 'Gerencial',
        'theme_minimalist': 'Minimalista',
        'theme_modern': 'Moderno',
        'theme_solar': 'Sistema Solar',
        'menu_language': 'Idioma',
        'force_tls': 'Forçar TLS 1.0/AES-128-CBC',
        'anti_suspend': 'Modo anti-suspensão (30s)',
        'show_console_log': 'Mostrar log do console',
        'notification_connected': 'Conectado à VPN',
        'yes': 'Sim',
        'no': 'Não',
        'tls_error_title': 'Erro de TLS Deprecado',
        'tls_error_msg': 'Um erro de TLS deprecado foi detectado.\n\nDeseja ativar o uso de TLS 1.0 com Criptografia AES-128-CBC?\n\nIsso pode resolver problemas de compatibilidade com servidores antigos.',
        'menu_help': 'Ajuda',
        'help_manual': 'Manual do VPN Linux Desktop Connector',
        'help_report_bug': 'Reportar um Erro',
        'help_donate': 'Fazer uma Doação',
        'help_about': 'Sobre o VPN Linux Desktop Connector',
        'lang_spanish': 'Espanhol',
        'lang_chinese': 'Chinês',
        'lang_portuguese': 'Português',
        'lang_french': 'Francês',
        'lang_german': 'Alemão',
        'lang_english': 'Inglês',
        'lang_japanese': 'Japonês',
        'lang_native_es': 'Español',
        'lang_native_zh': '中文',
        'lang_native_pt': 'Português',
        'lang_native_fr': 'Français',
        'lang_native_de': 'Deutsch',
        'lang_native_en': 'English',
        'lang_native_ja': '日本語',
        'label_user': 'Usuário:',
        'label_password': 'Senha:',
        'label_ovpn': 'Arquivo OVPN:',
        'placeholder_user': 'Digite o usuário',
        'placeholder_password': 'Digite a senha',
        'btn_select_ovpn': 'Selecionar arquivo OVPN',
        'btn_connect': 'Conectar VPN',
        'btn_disconnect': 'Desconectar VPN',
        'btn_connecting': 'Conectando VPN',
        'btn_disconnecting': 'Desconectando VPN',
        'btn_clear': 'Limpar Logs',
        'status': 'Estado:',
        'status_disconnected': 'Desconectado',
        'status_connecting': 'Conectando...',
        'status_connected': 'Conectado ✓',
        'status_disconnecting': 'Desconectando...',
        'initial_msg': "Pressione 'Conectar VPN' para iniciar a conexão.\n",
        'dialog_select_ovpn': 'Selecionar arquivo OVPN',
        'filter_ovpn': 'Arquivos OVPN',
        'filter_all': 'Todos os arquivos',
        'file_selected': 'Arquivo OVPN selecionado:',
        'error_required': 'Campos obrigatórios',
        'error_required_msg': 'Por favor, digite o usuário e a senha.',
        'error_ovpn_required': 'Arquivo OVPN obrigatório',
        'error_ovpn_required_msg': 'Por favor, selecione um arquivo OVPN.',
        'starting_connection': '=== Iniciando conexão VPN ===\n',
        'user': 'Usuário:',
        'credentials_saved': 'Credenciais salvas em config.txt\n\n',
        'disconnecting_vpn': '\n=== Desconectando VPN (Ctrl+C) ===\n',
        'vpn_disconnected': '\n=== VPN Desconectada ===\n',
        'connection_error': '\n=== Erro ao conectar ===\n',
        'vpn_disconnected_ok': '\n=== VPN desconectada corretamente ===\n',
        'vpn_disconnected_error': '\n=== VPN desconectada (com erros) ===\n',
        'process_ended': '\n=== Processo terminado com código',
        'error': 'Erro:',
        'error_connection_title': 'Erro de conexão',
        'error_connection_msg': 'Não é possível conectar com os parâmetros selecionados.\n\nVerifique:\n- Usuário e senha corretos\n- Arquivo OVPN válido\n- Conexão com a internet',
    },
    'fr': {
        'title': 'Connexion VPN - OpenVPN',
        'menu_config': 'Configuration',
        'menu_themes': 'Thèmes',
        'theme_managerial': 'Gestionnaire',
        'theme_minimalist': 'Minimaliste',
        'theme_modern': 'Moderne',
        'theme_solar': 'Système Solaire',
        'menu_language': 'Langue',
        'force_tls': 'Forcer TLS 1.0/AES-128-CBC',
        'anti_suspend': 'Mode anti-suspension (30s)',
        'show_console_log': 'Afficher le journal de la console',
        'notification_connected': 'Connecté au VPN',
        'yes': 'Oui',
        'no': 'Non',
        'tls_error_title': 'Erreur TLS Déprécié',
        'tls_error_msg': 'Une erreur TLS déprécié a été détectée.\n\nVoulez-vous activer TLS 1.0 avec le chiffrement AES-128-CBC?\n\nCela peut résoudre les problèmes de compatibilité avec les serveurs anciens.',
        'menu_help': 'Aide',
        'help_manual': 'Manuel de VPN Linux Desktop Connector',
        'help_report_bug': 'Signaler un Bug',
        'help_donate': 'Faire un Don',
        'help_about': 'À propos de VPN Linux Desktop Connector',
        'lang_spanish': 'Espagnol',
        'lang_chinese': 'Chinois',
        'lang_portuguese': 'Portugais',
        'lang_french': 'Français',
        'lang_german': 'Allemand',
        'lang_english': 'Anglais',
        'lang_japanese': 'Japonais',
        'lang_native_es': 'Español',
        'lang_native_zh': '中文',
        'lang_native_pt': 'Português',
        'lang_native_fr': 'Français',
        'lang_native_de': 'Deutsch',
        'lang_native_en': 'English',
        'lang_native_ja': '日本語',
        'label_user': 'Utilisateur:',
        'label_password': 'Mot de passe:',
        'label_ovpn': 'Fichier OVPN:',
        'placeholder_user': 'Entrez l\'utilisateur',
        'placeholder_password': 'Entrez le mot de passe',
        'btn_select_ovpn': 'Sélectionner fichier OVPN',
        'btn_connect': 'Connecter VPN',
        'btn_disconnect': 'Déconnecter VPN',
        'btn_connecting': 'Connexion VPN',
        'btn_disconnecting': 'Déconnexion VPN',
        'btn_clear': 'Effacer les journaux',
        'status': 'État:',
        'status_disconnected': 'Déconnecté',
        'status_connecting': 'Connexion...',
        'status_connected': 'Connecté ✓',
        'status_disconnecting': 'Déconnexion...',
        'initial_msg': "Appuyez sur 'Connecter VPN' pour démarrer la connexion.\n",
        'dialog_select_ovpn': 'Sélectionner fichier OVPN',
        'filter_ovpn': 'Fichiers OVPN',
        'filter_all': 'Tous les fichiers',
        'file_selected': 'Fichier OVPN sélectionné:',
        'error_required': 'Champs requis',
        'error_required_msg': 'Veuillez saisir l\'utilisateur et le mot de passe.',
        'error_ovpn_required': 'Fichier OVPN requis',
        'error_ovpn_required_msg': 'Veuillez sélectionner un fichier OVPN.',
        'starting_connection': '=== Démarrage de la connexion VPN ===\n',
        'user': 'Utilisateur:',
        'credentials_saved': 'Informations enregistrées dans config.txt\n\n',
        'disconnecting_vpn': '\n=== Déconnexion VPN (Ctrl+C) ===\n',
        'vpn_disconnected': '\n=== VPN Déconnecté ===\n',
        'connection_error': '\n=== Erreur de connexion ===\n',
        'vpn_disconnected_ok': '\n=== VPN déconnecté avec succès ===\n',
        'vpn_disconnected_error': '\n=== VPN déconnecté (avec erreurs) ===\n',
        'process_ended': '\n=== Processus terminé avec code',
        'error': 'Erreur:',
        'error_connection_title': 'Erreur de connexion',
        'error_connection_msg': 'Impossible de se connecter avec les paramètres sélectionnés.\n\nVérifiez:\n- Utilisateur et mot de passe corrects\n- Fichier OVPN valide\n- Connexion Internet',
    },
    'de': {
        'title': 'VPN-Verbindung - OpenVPN',
        'menu_config': 'Konfiguration',
        'menu_themes': 'Themen',
        'theme_managerial': 'Geschäftlich',
        'theme_minimalist': 'Minimalistisch',
        'theme_modern': 'Modern',
        'theme_solar': 'Sonnensystem',
        'menu_language': 'Sprache',
        'force_tls': 'TLS 1.0/AES-128-CBC erzwingen',
        'anti_suspend': 'Anti-Suspend-Modus (30s)',
        'show_console_log': 'Konsolenprotokoll anzeigen',
        'notification_connected': 'Mit VPN verbunden',
        'yes': 'Ja',
        'no': 'Nein',
        'tls_error_title': 'Veralteter TLS-Fehler',
        'tls_error_msg': 'Ein veralteter TLS-Fehler wurde erkannt.\n\nMöchten Sie TLS 1.0 mit AES-128-CBC-Verschlüsselung aktivieren?\n\nDies kann Kompatibilitätsprobleme mit älteren Servern lösen.',
        'menu_help': 'Hilfe',
        'help_manual': 'VPN Linux Desktop Connector Handbuch',
        'help_report_bug': 'Fehler melden',
        'help_donate': 'Spenden',
        'help_about': 'Über VPN Linux Desktop Connector',
        'lang_spanish': 'Spanisch',
        'lang_chinese': 'Chinesisch',
        'lang_portuguese': 'Portugiesisch',
        'lang_french': 'Französisch',
        'lang_german': 'Deutsch',
        'lang_english': 'Englisch',
        'lang_japanese': 'Japanisch',
        'lang_native_es': 'Español',
        'lang_native_zh': '中文',
        'lang_native_pt': 'Português',
        'lang_native_fr': 'Français',
        'lang_native_de': 'Deutsch',
        'lang_native_en': 'English',
        'lang_native_ja': '日本語',
        'label_user': 'Benutzer:',
        'label_password': 'Passwort:',
        'label_ovpn': 'OVPN-Datei:',
        'placeholder_user': 'Benutzer eingeben',
        'placeholder_password': 'Passwort eingeben',
        'btn_select_ovpn': 'OVPN-Datei auswählen',
        'btn_connect': 'VPN verbinden',
        'btn_disconnect': 'VPN trennen',
        'btn_connecting': 'VPN verbinden...',
        'btn_disconnecting': 'VPN trennen...',
        'btn_clear': 'Protokolle löschen',
        'status': 'Status:',
        'status_disconnected': 'Getrennt',
        'status_connecting': 'Verbinde...',
        'status_connected': 'Verbunden ✓',
        'status_disconnecting': 'Trennen...',
        'initial_msg': "Drücken Sie 'VPN verbinden', um die Verbindung zu starten.\n",
        'dialog_select_ovpn': 'OVPN-Datei auswählen',
        'filter_ovpn': 'OVPN-Dateien',
        'filter_all': 'Alle Dateien',
        'file_selected': 'OVPN-Datei ausgewählt:',
        'error_required': 'Pflichtfelder',
        'error_required_msg': 'Bitte geben Sie Benutzer und Passwort ein.',
        'error_ovpn_required': 'OVPN-Datei erforderlich',
        'error_ovpn_required_msg': 'Bitte wählen Sie eine OVPN-Datei aus.',
        'starting_connection': '=== VPN-Verbindung wird gestartet ===\n',
        'user': 'Benutzer:',
        'credentials_saved': 'Anmeldedaten in config.txt gespeichert\n\n',
        'disconnecting_vpn': '\n=== VPN trennen (Ctrl+C) ===\n',
        'vpn_disconnected': '\n=== VPN getrennt ===\n',
        'connection_error': '\n=== Verbindungsfehler ===\n',
        'vpn_disconnected_ok': '\n=== VPN erfolgreich getrennt ===\n',
        'vpn_disconnected_error': '\n=== VPN getrennt (mit Fehlern) ===\n',
        'process_ended': '\n=== Prozess beendet mit Code',
        'error': 'Fehler:',
        'error_connection_title': 'Verbindungsfehler',
        'error_connection_msg': 'Verbindung mit den ausgewählten Parametern nicht möglich.\n\nÜberprüfen Sie:\n- Benutzer und Passwort korrekt\n- Gültige OVPN-Datei\n- Internetverbindung',
    },
    'ja': {
        'title': 'VPN接続 - OpenVPN',
        'menu_config': '設定',
        'menu_themes': 'テーマ',
        'theme_managerial': 'ビジネス',
        'theme_minimalist': 'ミニマリスト',
        'theme_modern': 'モダン',
        'theme_solar': '太陽系',
        'menu_language': '言語',
        'force_tls': 'TLS 1.0/AES-128-CBC を強制',
        'anti_suspend': 'アンチサスペンドモード (30秒)',
        'show_console_log': 'コンソールログを表示',
        'notification_connected': 'VPNに接続しました',
        'yes': 'はい',
        'no': 'いいえ',
        'tls_error_title': '非推奨TLSエラー',
        'tls_error_msg': '非推奨のTLSエラーが検出されました。\n\nAES-128-CBC暗号化でTLS 1.0を有効にしますか？\n\nこれにより、古いサーバーとの互換性の問題が解決される場合があります。',
        'menu_help': 'ヘルプ',
        'help_manual': 'VPN Linux Desktop Connector マニュアル',
        'help_report_bug': 'バグを報告',
        'help_donate': '寄付する',
        'help_about': 'VPN Linux Desktop Connector について',
        'lang_spanish': 'スペイン語',
        'lang_chinese': '中国語',
        'lang_portuguese': 'ポルトガル語',
        'lang_french': 'フランス語',
        'lang_german': 'ドイツ語',
        'lang_english': '英語',
        'lang_japanese': '日本語',
        'lang_native_es': 'Español',
        'lang_native_zh': '中文',
        'lang_native_pt': 'Português',
        'lang_native_fr': 'Français',
        'lang_native_de': 'Deutsch',
        'lang_native_en': 'English',
        'lang_native_ja': '日本語',
        'label_user': 'ユーザー名：',
        'label_password': 'パスワード：',
        'label_ovpn': 'OVPNファイル：',
        'placeholder_user': 'ユーザー名を入力',
        'placeholder_password': 'パスワードを入力',
        'btn_select_ovpn': 'OVPNファイルを選択',
        'btn_connect': 'VPN接続',
        'btn_disconnect': 'VPN切断',
        'btn_connecting': 'VPN接続中',
        'btn_disconnecting': 'VPN切断中',
        'btn_clear': 'ログをクリア',
        'status': 'ステータス：',
        'status_disconnected': '切断済み',
        'status_connecting': '接続中...',
        'status_connected': '接続済み ✓',
        'status_disconnecting': '切断中...',
        'initial_msg': "'VPN接続'を押して接続を開始してください。\n",
        'dialog_select_ovpn': 'OVPNファイルを選択',
        'filter_ovpn': 'OVPNファイル',
        'filter_all': 'すべてのファイル',
        'file_selected': 'OVPNファイルが選択されました：',
        'error_required': '必須フィールド',
        'error_required_msg': 'ユーザー名とパスワードを入力してください。',
        'error_ovpn_required': 'OVPNファイルが必要です',
        'error_ovpn_required_msg': 'OVPNファイルを選択してください。',
        'starting_connection': '=== VPN接続を開始しています ===\n',
        'user': 'ユーザー：',
        'credentials_saved': '認証情報がconfig.txtに保存されました\n\n',
        'disconnecting_vpn': '\n=== VPNを切断しています (Ctrl+C) ===\n',
        'vpn_disconnected': '\n=== VPN切断済み ===\n',
        'connection_error': '\n=== 接続エラー ===\n',
        'vpn_disconnected_ok': '\n=== VPNが正常に切断されました ===\n',
        'vpn_disconnected_error': '\n=== VPNが切断されました（エラーあり）===\n',
        'process_ended': '\n=== プロセスが終了しました コード',
        'error': 'エラー：',
        'error_connection_title': '接続エラー',
        'error_connection_msg': '選択したパラメータで接続できません。\n\n確認事項：\n- ユーザー名とパスワードが正しい\n- 有効なOVPNファイル\n- インターネット接続',
    }
}

# Funciones de encriptación
def obtener_clave_encriptacion():
    """Genera u obtiene la clave de encriptación"""
    archivo_clave = '.vpn_key'

    # Si existe la clave, cargarla
    if os.path.exists(archivo_clave):
        with open(archivo_clave, 'rb') as f:
            return f.read()

    # Si no existe, generar una nueva clave basada en información del sistema
    # Usamos una combinación de información del sistema como "salt"
    salt = os.urandom(16)

    # Derivar una clave usando PBKDF2HMAC
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    # Usar el nombre de usuario y el hostname como base
    import getpass
    import socket
    base_string = f"{getpass.getuser()}-{socket.gethostname()}".encode()
    key = base64.urlsafe_b64encode(kdf.derive(base_string))

    # Guardar la clave y el salt
    with open(archivo_clave, 'wb') as f:
        f.write(salt + key)

    # Hacer el archivo oculto y con permisos restringidos
    os.chmod(archivo_clave, 0o600)

    return salt + key

def encriptar_password(password):
    """Encripta una contraseña"""
    try:
        datos_clave = obtener_clave_encriptacion()
        # Extraer solo la clave (después del salt)
        clave = datos_clave[16:]

        f = Fernet(clave)
        password_bytes = password.encode()
        password_encriptada = f.encrypt(password_bytes)
        return base64.urlsafe_b64encode(password_encriptada).decode()
    except Exception as e:
        print(f"Error al encriptar: {e}")
        return password

def desencriptar_password(password_encriptada):
    """Desencripta una contraseña"""
    try:
        datos_clave = obtener_clave_encriptacion()
        # Extraer solo la clave (después del salt)
        clave = datos_clave[16:]

        f = Fernet(clave)
        password_bytes = base64.urlsafe_b64decode(password_encriptada.encode())
        password_desencriptada = f.decrypt(password_bytes)
        return password_desencriptada.decode()
    except Exception as e:
        # Si falla la desencriptación, asumir que es texto plano (legacy)
        print(f"Error al desencriptar (posible texto plano): {e}")
        return password_encriptada

def obtener_ip_local():
    """Obtiene la dirección IP local"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
        return ip_local
    except Exception:
        return "No disponible"

def obtener_ip_publica():
    """Obtiene la dirección IP pública"""
    if not REQUESTS_AVAILABLE:
        return "No disponible (instalar requests)"

    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=3)
        return response.json()['ip']
    except Exception:
        return "No disponible"

def obtener_ip_vpn():
    """Obtiene la dirección IP del túnel VPN"""
    try:
        result = subprocess.run(['ip', 'addr', 'show', 'tun0'],
                              capture_output=True, text=True, timeout=2)
        for line in result.stdout.split('\n'):
            if 'inet ' in line:
                ip = line.strip().split()[1].split('/')[0]
                return ip
        return "No conectado"
    except Exception:
        return "No conectado"

def obtener_tipo_conexion():
    """Obtiene el tipo de conexión (WiFi o Ethernet) y nombre de red"""
    try:
        # Intentar obtener información de conexión con nmcli
        result = subprocess.run(['nmcli', '-t', '-f', 'TYPE,NAME,DEVICE', 'connection', 'show', '--active'],
                              capture_output=True, text=True, timeout=2)

        for line in result.stdout.split('\n'):
            if line:
                parts = line.split(':')
                if len(parts) >= 3:
                    tipo = parts[0]
                    nombre = parts[1]

                    if 'wireless' in tipo or '802-11-wireless' in tipo:
                        return f"WiFi ({nombre})"
                    elif 'ethernet' in tipo or '802-3-ethernet' in tipo:
                        return "Ethernet"

        return "No disponible"
    except Exception:
        return "No disponible"

class VentanaVPN(Gtk.Window):
    def __init__(self):
        super().__init__(title="VPN Linux Desktop Connector")
        self.set_default_size(300, 320)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)  # Eliminar botón maximizar y deshabilitar redimensionamiento

        # Establecer WM_CLASS para que el gestor de ventanas reconozca la aplicación
        self.set_wmclass("VPN-Linux-Desktop-Connector", "VPN-Linux-Desktop-Connector")

        self.proceso = None
        self.archivo_ovpn = None

        # Establecer ícono de la ventana y de la aplicación para la barra de tareas
        try:
            from gi.repository import GdkPixbuf
            # Intentar con PNG primero (más compatible con la barra de tareas)
            icon_path_png = os.path.join(os.path.dirname(__file__), "icons", "ico-index.png")
            icon_path_svg = os.path.join(os.path.dirname(__file__), "icons", "VPN-LDC_32x32.svg")

            if os.path.exists(icon_path_png):
                # Cargar PNG con GdkPixbuf (más compatible)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path_png, 64, 64, True)
                # Establecer ícono por defecto para la aplicación
                Gtk.Window.set_default_icon(pixbuf)
                # Establecer ícono de esta ventana
                self.set_icon(pixbuf)
            elif os.path.exists(icon_path_svg):
                # Fallback a SVG si PNG no existe
                Gtk.Window.set_default_icon_from_file(icon_path_svg)
                self.set_icon_from_file(icon_path_svg)
        except Exception as e:
            print(f"No se pudo cargar el ícono: {e}")

        # Idioma por defecto
        self.idioma_actual = 'es'
        self.cargar_idioma_guardado()

        # Tema por defecto
        self.tema_actual = 'modern'
        self.css_provider = None

        # Configuración de TLS
        self.force_tls = False
        self.cargar_config_tls()

        # Configuración de modo anti-suspensión
        self.anti_suspend_enabled = False
        self.anti_suspend_timer_id = None
        self.cargar_config_anti_suspend()

        # Configuración de mostrar log de consola
        self.show_console_log = False
        self.cargar_config_console_log()

        # Contenedor principal con menú
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # Crear barra de menú
        menubar = Gtk.MenuBar()
        main_vbox.pack_start(menubar, False, False, 0)

        # Menú Configuración
        self.menu_config_item = Gtk.MenuItem(label=self.t('menu_config'))
        menubar.append(self.menu_config_item)

        config_menu = Gtk.Menu()
        self.menu_config_item.set_submenu(config_menu)

        # Submenú Temas
        self.menu_temas_item = Gtk.MenuItem()
        temas_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        temas_icon = Gtk.Image.new_from_icon_name('preferences-desktop-theme', Gtk.IconSize.MENU)
        self.temas_label = Gtk.Label(label=self.t('menu_themes'))
        self.temas_label.set_xalign(0)
        temas_box.pack_start(temas_icon, False, False, 0)
        temas_box.pack_start(self.temas_label, True, True, 0)
        self.menu_temas_item.add(temas_box)
        config_menu.append(self.menu_temas_item)

        self.temas_submenu = Gtk.Menu()
        self.menu_temas_item.set_submenu(self.temas_submenu)

        # Opciones de temas con íconos
        self.temas_info = [
            ('managerial', 'theme_managerial', 'x-office-document'),
            ('minimalist', 'theme_minimalist', 'view-list-compact-symbolic'),
            ('modern', 'theme_modern', 'preferences-desktop-display'),
            ('solar', 'theme_solar', 'weather-clear-night')
        ]

        self.tema_menu_items = {}
        self.tema_checkmarks = {}
        for codigo, label_key, icono in self.temas_info:
            item = Gtk.MenuItem()
            tema_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

            # Ícono del tema
            tema_icon = Gtk.Image.new_from_icon_name(icono, Gtk.IconSize.MENU)
            tema_box.pack_start(tema_icon, False, False, 0)

            # Etiqueta del tema
            tema_label = Gtk.Label(label=self.t(label_key))
            tema_label.set_xalign(0)
            tema_box.pack_start(tema_label, True, True, 0)

            # Ícono de checkmark a la derecha (inicialmente invisible)
            checkmark = Gtk.Image.new_from_icon_name('emblem-default', Gtk.IconSize.MENU)
            checkmark.set_no_show_all(True)
            checkmark.hide()
            tema_box.pack_end(checkmark, False, False, 0)

            item.add(tema_box)
            item.connect('activate', self.cambiar_tema, codigo)
            self.temas_submenu.append(item)
            self.tema_menu_items[codigo] = (item, tema_label)
            self.tema_checkmarks[codigo] = checkmark

        # Submenú Idioma
        self.menu_idioma_item = Gtk.MenuItem()
        idioma_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        idioma_icon = Gtk.Image.new_from_icon_name('preferences-desktop-locale', Gtk.IconSize.MENU)
        self.idioma_label = Gtk.Label(label=self.t('menu_language'))
        self.idioma_label.set_xalign(0)
        idioma_box.pack_start(idioma_icon, False, False, 0)
        idioma_box.pack_start(self.idioma_label, True, True, 0)
        self.menu_idioma_item.add(idioma_box)
        config_menu.append(self.menu_idioma_item)

        self.idioma_submenu = Gtk.Menu()
        self.menu_idioma_item.set_submenu(self.idioma_submenu)

        # Opciones de idioma con banderas
        self.idiomas_info = [
            ('es', 'lang_spanish', 'lang_native_es', '🇨🇴'),
            ('zh', 'lang_chinese', 'lang_native_zh', '🇨🇳'),
            ('pt', 'lang_portuguese', 'lang_native_pt', '🇧🇷'),
            ('fr', 'lang_french', 'lang_native_fr', '🇫🇷'),
            ('de', 'lang_german', 'lang_native_de', '🇩🇪'),
            ('en', 'lang_english', 'lang_native_en', '🇬🇧'),
            ('ja', 'lang_japanese', 'lang_native_ja', '🇯🇵')
        ]

        self.idioma_menu_items = {}
        for codigo, label_key, native_key, bandera in self.idiomas_info:
            # Crear etiqueta con formato: "🏴 Nombre traducido (Nombre nativo)"
            if codigo == self.idioma_actual:
                # Si es el idioma actual, solo mostrar el nombre nativo con bandera
                etiqueta = f"{bandera}  {self.t(native_key)}"
            else:
                etiqueta = f"{bandera}  {self.t(label_key)} ({self.t(native_key)})"

            item = Gtk.MenuItem(label=etiqueta)
            item.connect('activate', self.cambiar_idioma, codigo)
            self.idioma_submenu.append(item)
            self.idioma_menu_items[codigo] = item

        # Opción: Forzar TLS 1.0
        self.menu_tls_item = Gtk.MenuItem()
        tls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        tls_icon = Gtk.Label()
        tls_icon.set_markup('<span font_size="11000" foreground="#FFB84D">🔒</span>')
        tls_icon.set_size_request(16, 16)  # Mismo tamaño que Gtk.IconSize.MENU
        tls_icon.set_xalign(0.5)
        tls_icon.set_yalign(0.5)
        tls_icon.set_margin_start(-4)  # Mover 4 píxeles a la izquierda
        self.tls_label = Gtk.Label(label=self.t('force_tls'))
        self.tls_label.set_xalign(0)
        self.tls_label.set_margin_start(-2)  # Mover 2 píxeles a la izquierda
        tls_box.pack_start(tls_icon, False, False, 0)
        tls_box.pack_start(self.tls_label, True, True, 0)

        # Agregar label de estado (Si/No) alineado a la derecha
        self.tls_status_label = Gtk.Label()
        self.actualizar_estado_tls()
        self.tls_status_label.set_xalign(1)
        tls_box.pack_end(self.tls_status_label, False, False, 10)

        self.menu_tls_item.add(tls_box)
        self.menu_tls_item.connect('activate', self.toggle_force_tls)
        config_menu.append(self.menu_tls_item)

        # Opción: Modo anti-suspensión
        self.menu_anti_suspend_item = Gtk.MenuItem()
        anti_suspend_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        anti_suspend_icon = Gtk.Label()
        anti_suspend_icon.set_markup('<span font_size="11000">🖱️</span>')
        anti_suspend_icon.set_size_request(16, 16)
        anti_suspend_icon.set_xalign(0.5)
        anti_suspend_icon.set_yalign(0.5)
        anti_suspend_icon.set_margin_start(-4)
        self.anti_suspend_label = Gtk.Label(label=self.t('anti_suspend'))
        self.anti_suspend_label.set_xalign(0)
        self.anti_suspend_label.set_margin_start(-2)
        anti_suspend_box.pack_start(anti_suspend_icon, False, False, 0)
        anti_suspend_box.pack_start(self.anti_suspend_label, True, True, 0)

        # Agregar label de estado (Si/No) alineado a la derecha
        self.anti_suspend_status_label = Gtk.Label()
        self.actualizar_estado_anti_suspend()
        self.anti_suspend_status_label.set_xalign(1)
        anti_suspend_box.pack_end(self.anti_suspend_status_label, False, False, 10)

        self.menu_anti_suspend_item.add(anti_suspend_box)
        self.menu_anti_suspend_item.connect('activate', self.toggle_anti_suspend)
        config_menu.append(self.menu_anti_suspend_item)

        # Opción: Mostrar log de consola
        self.menu_console_log_item = Gtk.MenuItem()
        console_log_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        console_log_icon = Gtk.Image.new_from_icon_name('utilities-terminal', Gtk.IconSize.MENU)
        self.console_log_label = Gtk.Label(label=self.t('show_console_log'))
        self.console_log_label.set_xalign(0)
        console_log_box.pack_start(console_log_icon, False, False, 0)
        console_log_box.pack_start(self.console_log_label, True, True, 0)

        # Agregar label de estado (Si/No) alineado a la derecha
        self.console_log_status_label = Gtk.Label()
        self.actualizar_estado_console_log()
        self.console_log_status_label.set_xalign(1)
        console_log_box.pack_end(self.console_log_status_label, False, False, 10)

        self.menu_console_log_item.add(console_log_box)
        self.menu_console_log_item.connect('activate', self.toggle_console_log)
        config_menu.append(self.menu_console_log_item)

        # Menú Ayuda
        self.menu_ayuda_item = Gtk.MenuItem(label=self.t('menu_help'))
        menubar.append(self.menu_ayuda_item)

        ayuda_menu = Gtk.Menu()
        self.menu_ayuda_item.set_submenu(ayuda_menu)

        # Opción: Manual (F1)
        manual_item = Gtk.MenuItem(label=self.t('help_manual') + '\t\tF1')
        manual_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        manual_icon = Gtk.Image.new_from_icon_name('help-contents', Gtk.IconSize.MENU)
        self.manual_label = Gtk.Label(label=self.t('help_manual'))
        self.manual_label.set_xalign(0)
        manual_box.pack_start(manual_icon, False, False, 0)
        manual_box.pack_start(self.manual_label, True, True, 0)
        manual_item.remove(manual_item.get_child())
        manual_item.add(manual_box)
        manual_item.connect('activate', self.on_manual_clicked)
        ayuda_menu.append(manual_item)

        # Opción: Informar de fallo
        bug_item = Gtk.MenuItem()
        bug_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        bug_icon = Gtk.Image.new_from_icon_name('dialog-warning', Gtk.IconSize.MENU)
        self.bug_label = Gtk.Label(label=self.t('help_report_bug'))
        self.bug_label.set_xalign(0)
        bug_box.pack_start(bug_icon, False, False, 0)
        bug_box.pack_start(self.bug_label, True, True, 0)
        bug_item.add(bug_box)
        bug_item.connect('activate', self.on_report_bug_clicked)
        ayuda_menu.append(bug_item)

        # Opción: Hacer un donativo
        donate_item = Gtk.MenuItem()
        donate_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        donate_icon = Gtk.Image.new_from_icon_name('emblem-favorite', Gtk.IconSize.MENU)
        self.donate_label = Gtk.Label(label=self.t('help_donate'))
        self.donate_label.set_xalign(0)
        donate_box.pack_start(donate_icon, False, False, 0)
        donate_box.pack_start(self.donate_label, True, True, 0)
        donate_item.add(donate_box)
        donate_item.connect('activate', self.on_donate_clicked)
        ayuda_menu.append(donate_item)

        # Separador
        separator = Gtk.SeparatorMenuItem()
        ayuda_menu.append(separator)

        # Opción: Acerca de
        about_item = Gtk.MenuItem()
        about_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        about_icon = Gtk.Image.new_from_icon_name('help-about', Gtk.IconSize.MENU)
        self.about_label = Gtk.Label(label=self.t('help_about'))
        self.about_label.set_xalign(0)
        about_box.pack_start(about_icon, False, False, 0)
        about_box.pack_start(self.about_label, True, True, 0)
        about_item.add(about_box)
        about_item.connect('activate', self.on_about_clicked)
        ayuda_menu.append(about_item)

        # Configurar acelerador de teclado F1 para abrir el manual
        from gi.repository import Gdk
        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)
        manual_item.add_accelerator('activate', accel_group,
                                     Gdk.KEY_F1,
                                     0,
                                     Gtk.AccelFlags.VISIBLE)

        # Contenedor principal
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7)
        vbox.set_margin_top(7)
        vbox.set_margin_bottom(7)
        vbox.set_margin_start(7)
        vbox.set_margin_end(7)
        main_vbox.pack_start(vbox, True, True, 0)

        # Logo centrado en la parte superior
        icono_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        icono_box.set_halign(Gtk.Align.CENTER)
        icono_box.set_valign(Gtk.Align.CENTER)
        vbox.pack_start(icono_box, False, False, 5)

        # Cargar y mostrar el ícono
        try:
            from gi.repository import GdkPixbuf
            icon_path = os.path.join(os.path.dirname(__file__), "icons", "ico-index.png")
            if os.path.exists(icon_path):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 120, 120, True)
                imagen_icono = Gtk.Image.new_from_pixbuf(pixbuf)
                icono_box.pack_start(imagen_icono, False, False, 0)
        except Exception as e:
            print(f"No se pudo cargar el ícono ico-index.png: {e}")

        # Contenedor para Usuario (etiqueta + caja)
        usuario_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)

        # Etiqueta Usuario
        label_usuario = Gtk.Label()
        label_usuario.set_markup(f'<span size="small">{self.t("label_user")}</span>')
        label_usuario.set_halign(Gtk.Align.START)
        label_usuario.set_margin_start(10)
        usuario_container.pack_start(label_usuario, False, False, 0)

        # Campo de Usuario
        self.entry_usuario = Gtk.Entry()
        self.entry_usuario.set_name("compact-entry")
        self.entry_usuario.set_margin_start(10)
        self.entry_usuario.set_margin_end(10)
        usuario_container.pack_start(self.entry_usuario, False, False, 0)

        vbox.pack_start(usuario_container, False, False, 0)

        # Contenedor para Contraseña (etiqueta + caja)
        password_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)

        # Etiqueta Contraseña
        label_password = Gtk.Label()
        label_password.set_markup(f'<span size="small">{self.t("label_password")}</span>')
        label_password.set_halign(Gtk.Align.START)
        label_password.set_margin_start(10)
        password_container.pack_start(label_password, False, False, 0)

        # Campo de Contraseña
        self.entry_password = Gtk.Entry()
        self.entry_password.set_name("compact-entry")
        self.entry_password.set_visibility(False)  # Ocultar contraseña
        self.entry_password.set_invisible_char('*')  # Mostrar asteriscos
        self.entry_password.set_margin_start(10)
        self.entry_password.set_margin_end(10)

        # Agregar ícono de ojo dentro del campo de contraseña
        self.password_visible = False
        self.entry_password.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "view-reveal-symbolic")
        self.entry_password.set_icon_tooltip_text(Gtk.EntryIconPosition.SECONDARY, "Mostrar/Ocultar contraseña")
        self.entry_password.connect("icon-press", self.on_toggle_password_visibility)

        password_container.pack_start(self.entry_password, False, False, 0)

        vbox.pack_start(password_container, False, False, 0)

        # Contenedor horizontal para el ícono de archivo y el nombre del archivo
        hbox_archivo = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_archivo.set_halign(Gtk.Align.FILL)
        hbox_archivo.set_margin_start(10)
        hbox_archivo.set_margin_end(10)
        vbox.pack_start(hbox_archivo, False, False, 0)

        # Ícono selector de Archivo OVPN (carpeta clickeable sin borde)
        self.folder_eventbox = Gtk.EventBox()
        self.folder_icon = Gtk.Image.new_from_icon_name("folder-open", Gtk.IconSize.DIALOG)
        self.folder_icon.set_pixel_size(40)
        self.folder_eventbox.add(self.folder_icon)
        self.folder_eventbox.set_tooltip_text(self.t('btn_select_ovpn'))
        self.folder_eventbox.connect("button-press-event", self.on_seleccionar_ovpn_clicked)
        hbox_archivo.pack_start(self.folder_eventbox, False, False, 0)

        # Guardar referencia al eventbox como boton_seleccionar_ovpn para mantener compatibilidad
        self.boton_seleccionar_ovpn = self.folder_eventbox

        # Etiqueta para mostrar el nombre del archivo seleccionado
        self.label_archivo_seleccionado = Gtk.Label()
        self.label_archivo_seleccionado.set_markup('<span size="small">Seleccione el archivo ovpn</span>')
        self.label_archivo_seleccionado.set_halign(Gtk.Align.START)
        self.label_archivo_seleccionado.set_ellipsize(Pango.EllipsizeMode.END)
        self.label_archivo_seleccionado.set_line_wrap(False)
        self.label_archivo_seleccionado.set_max_width_chars(30)
        hbox_archivo.pack_start(self.label_archivo_seleccionado, True, True, 0)

        # Contenedor horizontal para botón conectar y semáforo
        hbox_controles = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_controles.set_halign(Gtk.Align.FILL)
        hbox_controles.set_margin_start(10)
        hbox_controles.set_margin_end(10)
        vbox.pack_start(hbox_controles, False, False, 0)

        # Botón combinado conectar/desconectar
        self.boton_conectar_desconectar = Gtk.Button(label=self.t('btn_connect'))
        self.boton_conectar_desconectar.set_size_request(-1, 40)  # -1 permite expansión horizontal
        self.boton_conectar_desconectar.connect("clicked", self.on_toggle_conexion_clicked)
        hbox_controles.pack_start(self.boton_conectar_desconectar, True, True, 0)

        # Semáforo de estado (candado - inicialmente rojo - desconectado)
        self.semaforo_image = Gtk.Image()
        red_icon_path = os.path.join(os.path.dirname(__file__), "icons", "red.fw.png")
        self.semaforo_image.set_from_file(red_icon_path)
        self.semaforo_image.set_size_request(40, 40)
        hbox_controles.pack_start(self.semaforo_image, False, False, 0)

        # Variable para rastrear el estado de conexión
        self.conectado = False

        # Crear textview y textbuffer para mostrar logs de consola
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_monospace(True)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.set_left_margin(5)
        self.textview.set_right_margin(5)
        self.textview.set_top_margin(5)
        self.textview.set_bottom_margin(5)

        # Agregar clase CSS específica para la consola
        self.textview.get_style_context().add_class("console-log")

        # Aplicar colores directamente con override (más prioridad)
        from gi.repository import Gdk

        # Fondo negro
        color_fondo = Gdk.RGBA()
        color_fondo.parse("#000000")
        self.textview.override_background_color(Gtk.StateFlags.NORMAL, color_fondo)

        # Texto verde brillante
        color_texto = Gdk.RGBA()
        color_texto.parse("#00ff00")
        self.textview.override_color(Gtk.StateFlags.NORMAL, color_texto)

        self.textbuffer = self.textview.get_buffer()

        # Crear una etiqueta de texto (tag) para el color verde
        self.tag_console = self.textbuffer.create_tag("console", foreground="#00ff00", family="monospace")

        # Establecer el texto inicial con el tag
        start_iter = self.textbuffer.get_start_iter()
        self.textbuffer.insert_with_tags_by_name(start_iter, self.t('initial_msg'), "console")

        # Crear ScrolledWindow para el textview (altura reducida a 70px)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_size_request(-1, 70)
        self.scrolled_window.set_margin_start(10)
        self.scrolled_window.set_margin_end(10)
        self.scrolled_window.set_margin_top(10)
        self.scrolled_window.set_margin_bottom(10)

        # Agregar un borde visible al scrolled window
        self.scrolled_window.set_shadow_type(Gtk.ShadowType.IN)

        self.scrolled_window.add(self.textview)
        vbox.pack_start(self.scrolled_window, True, True, 0)

        # Inicialmente ocultar el log de consola (se mostrará si está habilitado en config)
        self.scrolled_window.set_no_show_all(True)
        self.scrolled_window.hide()

        # Cargar credenciales si existen
        self.cargar_credenciales()

        # Cargar tema guardado y aplicarlo
        self.cargar_tema_guardado()
        self.aplicar_tema(self.tema_actual)
        self.actualizar_marcador_tema()

        # Actualizar visibilidad del log de consola según configuración
        self.actualizar_visibilidad_console_log()

        # Crear ícono de bandeja del sistema
        self.crear_status_icon()

        # Actualizar el menú del indicador periódicamente (cada 5 segundos)
        GLib.timeout_add_seconds(5, self.actualizar_menu_status_icon)

        # Conectar evento de eliminación de ventana
        self.connect("delete-event", self.on_ventana_cerrar)

    def t(self, key):
        """Obtiene la traducción para la clave especificada"""
        return TRADUCCIONES.get(self.idioma_actual, TRADUCCIONES['es']).get(key, key)

    def cargar_idioma_guardado(self):
        """Carga el idioma guardado desde el archivo de configuración"""
        try:
            if os.path.exists('idioma.txt'):
                with open('idioma.txt', 'r') as f:
                    idioma = f.read().strip()
                    if idioma in TRADUCCIONES:
                        self.idioma_actual = idioma
        except Exception:
            pass

    def guardar_idioma(self):
        """Guarda el idioma actual en un archivo"""
        try:
            with open('idioma.txt', 'w') as f:
                f.write(self.idioma_actual)
        except Exception:
            pass

    def cargar_tema_guardado(self):
        """Carga el tema guardado desde el archivo de configuración"""
        try:
            if os.path.exists('tema.txt'):
                with open('tema.txt', 'r') as f:
                    tema = f.read().strip()
                    temas_validos = ['managerial', 'minimalist', 'modern', 'solar']
                    if tema in temas_validos:
                        self.tema_actual = tema
        except Exception:
            pass

    def guardar_tema(self):
        """Guarda el tema actual en un archivo"""
        try:
            with open('tema.txt', 'w') as f:
                f.write(self.tema_actual)
        except Exception:
            pass

    def actualizar_marcador_tema(self):
        """Actualiza el checkmark del tema activo"""
        for codigo, checkmark in self.tema_checkmarks.items():
            if codigo == self.tema_actual:
                checkmark.show()
            else:
                checkmark.hide()

    def cambiar_tema(self, widget, codigo_tema):
        """Cambia el tema de la aplicación"""
        self.tema_actual = codigo_tema
        self.guardar_tema()
        self.aplicar_tema(codigo_tema)
        self.actualizar_marcador_tema()

    def cargar_config_tls(self):
        """Carga la configuración de TLS desde el archivo"""
        try:
            if os.path.exists('tls_config.txt'):
                with open('tls_config.txt', 'r') as f:
                    valor = f.read().strip()
                    self.force_tls = (valor == 'true')
        except Exception:
            pass

    def guardar_config_tls(self):
        """Guarda la configuración de TLS en un archivo"""
        try:
            with open('tls_config.txt', 'w') as f:
                f.write('true' if self.force_tls else 'false')
        except Exception:
            pass

    def toggle_force_tls(self, widget):
        """Alterna el estado de forzar TLS 1.0"""
        self.force_tls = not self.force_tls
        self.guardar_config_tls()
        self.actualizar_estado_tls()

    def actualizar_estado_tls(self):
        """Actualiza el label de estado TLS (Si/No)"""
        estado = self.t('yes') if self.force_tls else self.t('no')
        self.tls_status_label.set_text(estado)

    def activar_tls_desde_error(self):
        """Activa TLS 1.0 y actualiza el menú"""
        self.force_tls = True
        self.guardar_config_tls()
        self.actualizar_estado_tls()

    def cargar_config_anti_suspend(self):
        """Carga la configuración de modo anti-suspensión desde el archivo"""
        try:
            if os.path.exists('anti_suspend_config.txt'):
                with open('anti_suspend_config.txt', 'r') as f:
                    valor = f.read().strip()
                    self.anti_suspend_enabled = (valor == 'true')
                    if self.anti_suspend_enabled:
                        self.iniciar_anti_suspend()
        except Exception:
            pass

    def guardar_config_anti_suspend(self):
        """Guarda la configuración de modo anti-suspensión en un archivo"""
        try:
            with open('anti_suspend_config.txt', 'w') as f:
                f.write('true' if self.anti_suspend_enabled else 'false')
        except Exception:
            pass

    def toggle_anti_suspend(self, widget):
        """Alterna el estado del modo anti-suspensión"""
        self.anti_suspend_enabled = not self.anti_suspend_enabled
        self.guardar_config_anti_suspend()
        self.actualizar_estado_anti_suspend()

        if self.anti_suspend_enabled:
            self.iniciar_anti_suspend()
        else:
            self.detener_anti_suspend()

    def actualizar_estado_anti_suspend(self):
        """Actualiza el label de estado del modo anti-suspensión (Si/No)"""
        estado = self.t('yes') if self.anti_suspend_enabled else self.t('no')
        self.anti_suspend_status_label.set_text(estado)

    def iniciar_anti_suspend(self):
        """Inicia el temporizador para mover el mouse cada 30 segundos"""
        if self.anti_suspend_timer_id:
            GLib.source_remove(self.anti_suspend_timer_id)
        # Iniciar temporizador de 30 segundos (30000 ms)
        self.anti_suspend_timer_id = GLib.timeout_add(30000, self.mover_mouse_ligero)

    def detener_anti_suspend(self):
        """Detiene el temporizador del modo anti-suspensión"""
        if self.anti_suspend_timer_id:
            GLib.source_remove(self.anti_suspend_timer_id)
            self.anti_suspend_timer_id = None

    def cargar_config_console_log(self):
        """Carga la configuración de mostrar log de consola desde el archivo"""
        try:
            if os.path.exists('console_log_config.txt'):
                with open('console_log_config.txt', 'r') as f:
                    valor = f.read().strip()
                    self.show_console_log = (valor == 'true')
        except Exception:
            pass

    def guardar_config_console_log(self):
        """Guarda la configuración de mostrar log de consola en un archivo"""
        try:
            with open('console_log_config.txt', 'w') as f:
                f.write('true' if self.show_console_log else 'false')
        except Exception:
            pass

    def toggle_console_log(self, widget):
        """Alterna el estado de mostrar log de consola"""
        self.show_console_log = not self.show_console_log
        self.guardar_config_console_log()
        self.actualizar_estado_console_log()
        self.actualizar_visibilidad_console_log()

    def actualizar_estado_console_log(self):
        """Actualiza el label de estado de mostrar log de consola (Si/No)"""
        estado = self.t('yes') if self.show_console_log else self.t('no')
        self.console_log_status_label.set_text(estado)

    def actualizar_visibilidad_console_log(self):
        """Muestra u oculta el textview de log de consola según la configuración y ajusta el tamaño de la ventana"""
        # Obtener el ancho actual de la ventana
        ancho_actual = self.get_size()[0]

        if self.show_console_log:
            # Mostrar el log y expandir la ventana
            self.textview.show()  # Mostrar explícitamente el textview
            self.scrolled_window.show()
            self.resize(ancho_actual, 420)  # Altura expandida
        else:
            # Ocultar el log y contraer la ventana
            self.scrolled_window.hide()
            self.resize(ancho_actual, 320)  # Altura original

    def mover_mouse_ligero(self):
        """Mueve el mouse ligeramente de forma aleatoria"""
        import random
        from gi.repository import Gdk

        try:
            # Obtener el display y el dispositivo de puntero
            display = Gdk.Display.get_default()
            seat = display.get_default_seat()
            pointer = seat.get_pointer()

            # Obtener posición actual
            screen, x, y = pointer.get_position()

            # Mover ligeramente (entre -25 y 25 píxeles en cada dirección)
            dx = random.randint(-25, 25)
            dy = random.randint(-25, 25)

            # Calcular nueva posición
            new_x = x + dx
            new_y = y + dy

            # Mover el puntero
            pointer.warp(screen, new_x, new_y)

        except Exception as e:
            print(f"Error al mover el mouse: {e}")

        # Retornar True para que el temporizador continúe
        return True

    def aplicar_tema(self, tema):
        """Aplica el tema CSS seleccionado"""
        # Remover el provider anterior si existe
        if self.css_provider:
            Gtk.StyleContext.remove_provider_for_screen(
                self.get_screen(),
                self.css_provider
            )

        # Crear nuevo provider
        self.css_provider = Gtk.CssProvider()

        # Definir estilos CSS según el tema
        if tema == 'managerial':
            css = """
            window {
                background-color: #f0f4f8;
            }

            menubar {
                background-color: #6eb5e0;
                color: black;
                border-bottom: 2px solid #5a9fd4;
            }

            menubar > menuitem {
                color: black;
                padding: 6px 11px;
            }

            menubar > menuitem:hover {
                background-color: #8dc5e8;
            }

            menu {
                background-color: #ffffff;
                border: 1px solid #cbd5e0;
            }

            menuitem {
                padding: 6px 14px;
                color: #2d3748;
            }

            menuitem:hover {
                background-color: #e6f2ff;
                color: #2c5282;
            }

            entry {
                background-color: white;
                color: #2d3748;
                border: 2px solid #cbd5e0;
                border-radius: 4px;
                padding: 6px;
            }

            entry:focus {
                border-color: #4299e1;
                box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.3);
            }

            #compact-entry {
                padding: 2px 6px;
                min-height: 20px;
            }

            button {
                background-image: linear-gradient(to bottom, #8dc5e8, #6eb5e0);
                color: black;
                border: 1px solid #5a9fd4;
                border-radius: 4px;
                padding: 7px 14px;
                font-weight: bold;
            }

            button:hover {
                background-image: linear-gradient(to bottom, #a5d4ef, #8dc5e8);
            }

            button:disabled {
                background-image: none;
                background-color: #cbd5e0;
                color: #a0aec0;
            }

            textview {
                background-color: #ffffff;
                color: #2d3748;
                border: 1px solid #cbd5e0;
                font-size: 10px;
            }

            textview text {
                font-size: 10px;
            }

            /* Estilos específicos para la consola de logs */
            textview.console-log {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 2px solid #4a5568;
                font-family: monospace;
                font-size: 11px;
            }

            textview.console-log text {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: monospace;
                font-size: 11px;
            }

            label {
                color: #2d3748;
                font-weight: 500;
            }

            tooltip {
                background-color: #2d3748;
                color: white;
                border: 1px solid #1a202c;
                border-radius: 4px;
            }

            tooltip label {
                color: white;
            }
            """
        elif tema == 'minimalist':
            css = """
            window {
                background-color: #fafafa;
            }

            menubar {
                background-color: #ffffff;
                color: #333333;
                border-bottom: 1px solid #e0e0e0;
            }

            menubar > menuitem {
                color: #333333;
                padding: 6px 11px;
            }

            menubar > menuitem:hover {
                background-color: #f5f5f5;
            }

            menu {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
            }

            menuitem {
                padding: 6px 14px;
                color: #333333;
            }

            menuitem:hover {
                background-color: #f5f5f5;
            }

            entry {
                background-color: white;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 2px;
                padding: 6px;
            }

            entry:focus {
                border-color: #999999;
            }

            #compact-entry {
                padding: 2px 6px;
                min-height: 20px;
            }

            button {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 2px;
                padding: 7px 14px;
            }

            button:hover {
                background-color: #f5f5f5;
                border-color: #999999;
            }

            button:disabled {
                background-color: #fafafa;
                color: #bdbdbd;
            }

            textview {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #e0e0e0;
                font-size: 10px;
            }

            textview text {
                font-size: 10px;
            }

            /* Estilos específicos para la consola de logs */
            textview.console-log {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 2px solid #4a5568;
                font-family: monospace;
                font-size: 11px;
            }

            textview.console-log text {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: monospace;
                font-size: 11px;
            }

            label {
                color: #333333;
            }

            tooltip {
                background-color: #333333;
                color: white;
                border: 1px solid #1a1a1a;
                border-radius: 2px;
            }

            tooltip label {
                color: white;
            }
            """
        elif tema == 'modern':
            css = """
            window {
                background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
                background-color: #f8f9fd;
            }

            menubar {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-bottom: 2px solid rgba(102, 126, 234, 0.3);
                border-radius: 0;
            }

            menubar > menuitem {
                color: white;
                padding: 6px 11px;
                font-weight: 500;
            }

            menubar > menuitem:hover {
                background: rgba(255, 255, 255, 0.25);
                border-radius: 4px;
            }

            menu {
                background-color: #ffffff;
                border: 1px solid #c7d2fe;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }

            menuitem {
                padding: 6px 14px;
                color: #312e81;
                border-radius: 4px;
                font-weight: 500;
            }

            menuitem:hover {
                background: linear-gradient(90deg, #ede9fe 0%, #e0e7ff 100%);
                color: #4c1d95;
            }

            entry {
                background-color: white;
                color: #1e1b4b;
                border: 2px solid #c7d2fe;
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
                font-weight: 500;
            }

            entry:focus {
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
                background-color: #fafbff;
            }

            #compact-entry {
                padding: 2px 6px;
                min-height: 20px;
            }

            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 14px;
                font-weight: 600;
                font-size: 14px;
                box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
            }

            button:hover {
                background: linear-gradient(135deg, #5568d3 0%, #6b3f8e 100%);
                box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
            }

            button:active {
                background: linear-gradient(135deg, #4c5dc9 0%, #5c357a 100%);
                box-shadow: 0 1px 2px rgba(102, 126, 234, 0.3);
            }

            button:disabled {
                background: linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%);
                color: #64748b;
                box-shadow: none;
            }

            textview {
                background-color: #ffffff;
                color: #1e1b4b;
                border: 2px solid #c7d2fe;
                border-radius: 8px;
                font-size: 10px;
                font-weight: 500;
            }

            textview text {
                background-color: #ffffff;
                color: #1e1b4b;
                font-size: 10px;
            }

            /* Estilos específicos para la consola de logs */
            textview.console-log {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 2px solid #4a5568;
                font-family: monospace;
                font-size: 11px;
            }

            textview.console-log text {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: monospace;
                font-size: 11px;
            }

            label {
                color: #312e81;
                font-weight: 600;
            }

            tooltip {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: 1px solid #5568d3;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
            }

            tooltip label {
                color: white;
                font-weight: 500;
            }
            """
        elif tema == 'solar':
            css = """
            window {
                background-color: #0a0e1a;
                background: radial-gradient(ellipse at top, #1a1f3a 0%, #0a0e1a 50%, #000000 100%);
            }

            menubar {
                background: linear-gradient(90deg, #1a1f3a 0%, #2d1b3d 100%);
                color: #e8e8e8;
                border-bottom: 2px solid #4a5fe8;
            }

            menubar > menuitem {
                color: #e8e8e8;
                padding: 6px 11px;
                font-weight: 500;
            }

            menubar > menuitem:hover {
                background: rgba(74, 95, 232, 0.3);
                border-radius: 4px;
                box-shadow: 0 0 10px rgba(74, 95, 232, 0.5);
            }

            menu {
                background-color: #1a1d2e;
                border: 2px solid #4a5fe8;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(74, 95, 232, 0.3);
            }

            menuitem {
                padding: 6px 14px;
                color: #e8e8e8;
                border-radius: 4px;
            }

            menuitem:hover {
                background: linear-gradient(90deg, #2d1b3d 0%, #4a5fe8 100%);
                color: #ffffff;
                box-shadow: 0 0 8px rgba(74, 95, 232, 0.6);
            }

            entry {
                background-color: #1a1d2e;
                color: #e8e8e8;
                border: 2px solid #4a5fe8;
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
                caret-color: #ffb84d;
            }

            entry:focus {
                border-color: #ffb84d;
                box-shadow: 0 0 12px rgba(255, 149, 0, 0.6);
                background-color: #1f2333;
            }

            #compact-entry {
                padding: 2px 6px;
                min-height: 20px;
            }

            button {
                background: linear-gradient(135deg, #734500 0%, #8a5c00 30%, #a15c00 70%, #8a5c00 100%);
                color: #ffffff;
                border: 2px solid #8a5c00;
                border-radius: 8px;
                padding: 7px 14px;
                font-weight: 700;
                font-size: 14px;
                box-shadow: 0 4px 15px rgba(138, 92, 0, 0.5);
            }

            button:hover {
                background: linear-gradient(135deg, #8a5c00 0%, #a15c00 30%, #b86e00 70%, #a15c00 100%);
                color: #ffffff;
                border-color: #a15c00;
                box-shadow: 0 6px 20px rgba(161, 92, 0, 0.6);
            }

            button:active {
                background: linear-gradient(135deg, #5c3800 0%, #734500 50%, #5c3800 100%);
                color: #ffffff;
                box-shadow: 0 2px 8px rgba(115, 69, 0, 0.5);
            }

            button:disabled {
                background: linear-gradient(135deg, #3a3d4a 0%, #2d2f3a 100%);
                color: #5a5d6a;
                border-color: #3a3d4a;
                box-shadow: none;
            }

            textview {
                background-color: #0d1117;
                color: #e8e8e8;
                border: 2px solid #4a5fe8;
                border-radius: 8px;
                font-size: 10px;
                box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.5);
            }

            textview text {
                background-color: #0d1117;
                color: #e8e8e8;
                font-size: 10px;
            }

            /* Estilos específicos para la consola de logs */
            textview.console-log {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 2px solid #4a5568;
                font-family: monospace;
                font-size: 11px;
            }

            textview.console-log text {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: monospace;
                font-size: 11px;
            }

            label {
                color: #e8e8e8;
                font-weight: 600;
                text-shadow: 0 0 5px rgba(74, 95, 232, 0.5);
            }
            """

        # Cargar el CSS
        self.css_provider.load_from_data(css.encode())

        # Aplicar el provider a la pantalla
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def cambiar_idioma(self, widget, codigo_idioma):
        """Cambia el idioma de la aplicación"""
        self.idioma_actual = codigo_idioma
        self.guardar_idioma()
        self.actualizar_textos_interfaz()

    def actualizar_textos_interfaz(self):
        """Actualiza todos los textos de la interfaz según el idioma actual"""
        # Actualizar título de la ventana
        self.set_title(self.t('title'))

        # Actualizar menús
        self.menu_config_item.set_label(self.t('menu_config'))
        self.temas_label.set_text(self.t('menu_themes'))
        self.idioma_label.set_text(self.t('menu_language'))
        self.menu_ayuda_item.set_label(self.t('menu_help'))

        # Actualizar los items del menú de temas
        for codigo, label_key, icono in self.temas_info:
            item, tema_label = self.tema_menu_items[codigo]
            tema_label.set_text(self.t(label_key))

        # Actualizar los items del menú de idiomas con el formato correcto
        for codigo, label_key, native_key, bandera in self.idiomas_info:
            if codigo == self.idioma_actual:
                # Si es el idioma actual, solo mostrar el nombre nativo con bandera
                etiqueta = f"{bandera}  {self.t(native_key)}"
            else:
                # Mostrar "🏴 Nombre traducido (Nombre nativo)"
                etiqueta = f"{bandera}  {self.t(label_key)} ({self.t(native_key)})"
            self.idioma_menu_items[codigo].set_label(etiqueta)

        # Actualizar label de TLS
        self.tls_label.set_text(self.t('force_tls'))
        self.actualizar_estado_tls()

        # Actualizar label de modo anti-suspensión
        self.anti_suspend_label.set_text(self.t('anti_suspend'))
        self.actualizar_estado_anti_suspend()

        # Actualizar label de mostrar log de consola
        self.console_log_label.set_text(self.t('show_console_log'))
        self.actualizar_estado_console_log()

        # Actualizar labels del menú Ayuda
        self.manual_label.set_text(self.t('help_manual'))
        self.bug_label.set_text(self.t('help_report_bug'))
        self.donate_label.set_text(self.t('help_donate'))
        self.about_label.set_text(self.t('help_about'))

        # Actualizar placeholders (usando las etiquetas como placeholders)
        self.entry_usuario.set_placeholder_text(self.t('label_user').replace(':', ''))
        self.entry_password.set_placeholder_text(self.t('label_password').replace(':', ''))

        # Actualizar tooltip del botón selector OVPN
        if self.archivo_ovpn:
            # Si ya hay un archivo seleccionado, mostrar el nombre en el tooltip
            nombre_archivo = self.archivo_ovpn.split('/')[-1]
            self.boton_seleccionar_ovpn.set_tooltip_text(f"✓ {nombre_archivo}")
        else:
            # Si no hay archivo, mostrar texto predeterminado en el tooltip
            self.boton_seleccionar_ovpn.set_tooltip_text(self.t('btn_select_ovpn'))

        # Actualizar etiqueta del botón según el estado actual
        if self.conectado:
            self.boton_conectar_desconectar.set_label(self.t('btn_disconnect'))
        else:
            self.boton_conectar_desconectar.set_label(self.t('btn_connect'))

        # Actualizar semáforo según el estado actual
        if self.conectado:
            self.actualizar_semaforo('conectado')
        else:
            self.actualizar_semaforo('desconectado')

        # Actualizar mensaje inicial en el área de logs si está vacío o solo contiene el mensaje inicial
        current_text = self.textbuffer.get_text(
            self.textbuffer.get_start_iter(),
            self.textbuffer.get_end_iter(),
            True
        ).strip()

        # Verificar si el texto actual es un mensaje inicial en cualquier idioma
        mensajes_iniciales = [
            TRADUCCIONES[lang]['initial_msg'].strip()
            for lang in TRADUCCIONES.keys()
        ]

        # Si el buffer está vacío o contiene solo un mensaje inicial, actualizarlo
        if not current_text or current_text in mensajes_iniciales:
            self.textbuffer.set_text("")
            start_iter = self.textbuffer.get_start_iter()
            self.textbuffer.insert_with_tags_by_name(start_iter, self.t('initial_msg'), "console")

    def on_toggle_password_visibility(self, entry, icon_pos, event):
        """Alterna entre mostrar y ocultar la contraseña"""
        self.password_visible = not self.password_visible
        self.entry_password.set_visibility(self.password_visible)

        # Cambiar el ícono según el estado
        if self.password_visible:
            # Ojo tachado cuando la contraseña es visible
            self.entry_password.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "view-conceal-symbolic")
        else:
            # Ojo normal cuando la contraseña está oculta
            self.entry_password.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "view-reveal-symbolic")

    def on_seleccionar_ovpn_clicked(self, widget, event=None):
        """Abre un diálogo para seleccionar el archivo OVPN"""
        dialog = Gtk.FileChooserDialog(
            title=self.t('dialog_select_ovpn'),
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )

        # Filtro para archivos .ovpn
        filter_ovpn = Gtk.FileFilter()
        filter_ovpn.set_name(self.t('filter_ovpn'))
        filter_ovpn.add_pattern("*.ovpn")
        dialog.add_filter(filter_ovpn)

        # Filtro para todos los archivos
        filter_all = Gtk.FileFilter()
        filter_all.set_name(self.t('filter_all'))
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.archivo_ovpn = dialog.get_filename()
            nombre_archivo = self.archivo_ovpn.split('/')[-1]
            self.boton_seleccionar_ovpn.set_tooltip_text(f"✓ {nombre_archivo}")
            self.label_archivo_seleccionado.set_markup(f'<span size="small">{nombre_archivo}</span>')
            self.agregar_texto(f"{self.t('file_selected')} {self.archivo_ovpn}\n")

        dialog.destroy()

    def cargar_credenciales(self):
        """Carga las credenciales desde config.txt si existe y desencripta la contraseña"""
        try:
            with open("config.txt", "r") as f:
                lineas = f.readlines()
                if len(lineas) >= 1:
                    self.entry_usuario.set_text(lineas[0].strip())
                if len(lineas) >= 2:
                    # Desencriptar la contraseña antes de mostrarla
                    password_encriptada = lineas[1].strip()
                    password_desencriptada = desencriptar_password(password_encriptada)
                    self.entry_password.set_text(password_desencriptada)
                if len(lineas) >= 3:
                    self.archivo_ovpn = lineas[2].strip()
                    if self.archivo_ovpn:
                        nombre_archivo = self.archivo_ovpn.split('/')[-1]
                        self.boton_seleccionar_ovpn.set_tooltip_text(f"✓ {nombre_archivo}")
                        self.label_archivo_seleccionado.set_markup(f'<span size="small">{nombre_archivo}</span>')
        except FileNotFoundError:
            pass  # Si no existe el archivo, no hacer nada

    def guardar_credenciales(self):
        """Guarda las credenciales en config.txt con la contraseña encriptada"""
        usuario = self.entry_usuario.get_text()
        password = self.entry_password.get_text()

        # Encriptar la contraseña antes de guardarla
        password_encriptada = encriptar_password(password)

        with open("config.txt", "w") as f:
            f.write(usuario + "\n")
            f.write(password_encriptada + "\n")
            if self.archivo_ovpn:
                f.write(self.archivo_ovpn + "\n")

        # Proteger el archivo de configuración
        os.chmod("config.txt", 0o600)

        return usuario, password

    def on_conectar_clicked(self, widget):
        # Validar que los campos no estén vacíos
        usuario = self.entry_usuario.get_text().strip()
        password = self.entry_password.get_text().strip()

        if not usuario or not password:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text=self.t('error_required')
            )
            dialog.format_secondary_text(self.t('error_required_msg'))
            dialog.run()
            dialog.destroy()
            return

        if not self.archivo_ovpn:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text=self.t('error_ovpn_required')
            )
            dialog.format_secondary_text(self.t('error_ovpn_required_msg'))
            dialog.run()
            dialog.destroy()
            return

        # Guardar credenciales en config.txt
        self.guardar_credenciales()

        self.textbuffer.set_text("")
        self.agregar_texto(self.t('starting_connection'))
        self.agregar_texto(f"{self.t('user')} {usuario}\n")
        self.agregar_texto(self.t('credentials_saved'))
        self.actualizar_semaforo('conectando')

        # Estado: Conectando - Cambiar botón a "Conectando VPN"
        self.boton_conectar_desconectar.set_label(self.t('btn_connecting'))
        self.conectado = True

        # Ejecutar en un hilo separado
        thread = threading.Thread(target=self.ejecutar_vpn)
        thread.daemon = True
        thread.start()

    def on_desconectar_clicked(self, widget):
        if self.proceso and self.proceso.poll() is None:
            self.agregar_texto(self.t('disconnecting_vpn'))
            self.actualizar_semaforo('desconectando')

            # Cambiar botón a "Desconectando VPN" y deshabilitar
            self.boton_conectar_desconectar.set_label(self.t('btn_disconnecting'))
            self.boton_conectar_desconectar.set_sensitive(False)

            try:
                # Enviar SIGINT (Ctrl+C) en lugar de SIGTERM
                self.proceso.send_signal(signal.SIGINT)
                # Forzar terminación después de un momento
                threading.Thread(target=self.forzar_desconexion, daemon=True).start()
            except Exception as e:
                self.agregar_texto(f"{self.t('error')} {e}\n")
                GLib.idle_add(self.reactivar_botones)

    def forzar_desconexion(self):
        """Espera a que el proceso termine y actualiza el estado"""
        try:
            # Esperar hasta 5 segundos a que termine
            self.proceso.wait(timeout=5)
        except:
            # Si no termina, forzar con SIGKILL
            try:
                self.proceso.kill()
                self.proceso.wait()
            except:
                pass

        # Actualizar interfaz
        GLib.idle_add(self.agregar_texto, self.t('vpn_disconnected'))
        GLib.idle_add(self.reactivar_botones)

    def on_toggle_conexion_clicked(self, widget):
        """Función que alterna entre conectar y desconectar"""
        if self.conectado:
            # Si está conectado, desconectar
            self.on_desconectar_clicked(widget)
        else:
            # Si está desconectado, conectar
            self.on_conectar_clicked(widget)

    def ejecutar_vpn(self):
        try:
            # Crear archivo temporal con credenciales desencriptadas para OpenVPN
            import tempfile
            temp_config = None

            try:
                # Leer el config.txt y desencriptar la contraseña
                with open("config.txt", "r") as f:
                    lineas = f.readlines()
                    usuario = lineas[0].strip() if len(lineas) >= 1 else ""
                    password_encriptada = lineas[1].strip() if len(lineas) >= 2 else ""
                    password = desencriptar_password(password_encriptada)

                # Crear archivo temporal con permisos restringidos
                fd, temp_config = tempfile.mkstemp(prefix='.vpn_temp_', suffix='.txt', text=True)
                os.chmod(temp_config, 0o600)

                # Escribir credenciales desencriptadas
                with os.fdopen(fd, 'w') as f:
                    f.write(f"{usuario}\n{password}\n")

                # Construir comando base
                comando = f"sudo openvpn --config \"{self.archivo_ovpn}\" --auth-user-pass \"{temp_config}\""

                # Agregar parámetros TLS si está forzado
                if self.force_tls:
                    comando += ' --tls-version-max 1.0 --tls-cipher "DEFAULT:@SECLEVEL=0" --data-ciphers AES-128-CBC'
            except Exception as e:
                GLib.idle_add(self.agregar_texto, f"{self.t('error')} {e}\n")
                if temp_config and os.path.exists(temp_config):
                    os.unlink(temp_config)
                return

            self.proceso = subprocess.Popen(
                comando,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # Variables para detectar errores
            error_autenticacion = False
            error_archivo = False
            error_tls = False
            conectado_exitosamente = False

            # Leer la salida en tiempo real
            for linea in self.proceso.stdout:
                GLib.idle_add(self.agregar_texto, linea)

                # Detectar cuando se conecta exitosamente
                if "Initialization Sequence Completed" in linea:
                    GLib.idle_add(self.actualizar_estado_conectado)
                    conectado_exitosamente = True

                # Detectar errores de autenticación
                if "AUTH_FAILED" in linea or "auth-failure" in linea.lower():
                    error_autenticacion = True

                # Detectar errores de archivo/configuración
                if "No such file" in linea or "Cannot open" in linea or "Options error" in linea or "parse error" in linea:
                    error_archivo = True

                # Detectar errores de TLS deprecado
                if not self.force_tls and ("unsupported protocol" in linea.lower() or
                                           "wrong version number" in linea.lower() or
                                           "sslv3 alert handshake failure" in linea.lower() or
                                           "no shared cipher" in linea.lower() or
                                           "tls key negotiation failed" in linea.lower() or
                                           "tls handshake failed" in linea.lower()):
                    error_tls = True

            # Esperar a que termine
            self.proceso.wait()

            # Si hubo error de TLS, mostrar diálogo para activar TLS 1.0
            if error_tls:
                GLib.idle_add(self.agregar_texto, self.t('connection_error'))
                GLib.idle_add(self.mostrar_dialogo_tls)
            # Si hubo errores de autenticación o archivo, mostrar error
            elif error_autenticacion or error_archivo:
                GLib.idle_add(self.agregar_texto, self.t('connection_error'))
                GLib.idle_add(self.mostrar_error_conexion)
            # Si se conectó exitosamente y luego terminó, fue una desconexión correcta
            elif conectado_exitosamente and self.proceso.returncode == 0:
                GLib.idle_add(self.agregar_texto, self.t('vpn_disconnected_ok'))
            # Si nunca se conectó y el proceso falló, error de conexión
            elif not conectado_exitosamente and self.proceso.returncode != 0:
                GLib.idle_add(self.agregar_texto, self.t('connection_error'))
                GLib.idle_add(self.mostrar_error_conexion)
            # Si se conectó pero terminó con error
            elif conectado_exitosamente and self.proceso.returncode != 0:
                GLib.idle_add(self.agregar_texto, self.t('vpn_disconnected_error'))
            # Cualquier otro caso
            else:
                GLib.idle_add(self.agregar_texto, f"{self.t('process_ended')} {self.proceso.returncode} ===\n")

        except Exception as e:
            GLib.idle_add(self.agregar_texto, f"\n{self.t('error')} {e}\n")
            GLib.idle_add(self.agregar_texto, self.t('connection_error'))
            GLib.idle_add(self.mostrar_error_conexion)
        finally:
            # Limpiar el archivo temporal de credenciales
            if temp_config and os.path.exists(temp_config):
                try:
                    os.unlink(temp_config)
                except Exception:
                    pass
            GLib.idle_add(self.reactivar_botones)

    def actualizar_estado_conectado(self):
        # Estado: Conectado - Cambiar botón a "Desconectar"
        self.boton_conectar_desconectar.set_label(self.t('btn_disconnect'))
        self.boton_conectar_desconectar.set_sensitive(True)
        self.conectado = True
        self.actualizar_semaforo('conectado')

        # Ocultar ventana después de 1 segundo y mostrar notificación
        GLib.timeout_add(1000, self.ocultar_ventana_y_notificar)

        return False

    def ocultar_ventana_y_notificar(self):
        """Oculta la ventana y muestra una notificación de conexión exitosa"""
        # Ocultar la ventana (minimizar a la bandeja)
        self.hide()

        # Actualizar tooltip del status icon
        if hasattr(self, 'status_icon') and self.status_icon:
            try:
                self.status_icon.set_tooltip_text(self.t('notification_connected'))
            except:
                pass

        # Intentar mostrar notificación del sistema
        try:
            # Usar notify-send como comando del sistema
            subprocess.run(
                ['notify-send',
                 'VPN Linux Desktop Connector',
                 self.t('notification_connected'),
                 '-i', 'network-vpn',
                 '-t', '3000'],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except:
            pass

        return False

    def mostrar_error_conexion(self):
        """Muestra un diálogo de error cuando no se puede conectar"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=self.t('error_connection_title')
        )
        dialog.format_secondary_text(self.t('error_connection_msg'))
        dialog.run()
        dialog.destroy()
        return False

    def mostrar_dialogo_tls(self):
        """Muestra un diálogo preguntando si desea activar TLS 1.0"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=self.t('tls_error_title')
        )
        dialog.format_secondary_text(self.t('tls_error_msg'))
        response = dialog.run()
        dialog.destroy()

        # Si el usuario presiona "Sí", activar TLS 1.0
        if response == Gtk.ResponseType.YES:
            self.activar_tls_desde_error()
            self.agregar_texto(f"\n=== TLS 1.0/AES-128-CBC {self.t('yes')} ===\n")

        return False

    def agregar_texto(self, texto):
        end_iter = self.textbuffer.get_end_iter()
        # Insertar el texto con el tag "console" para aplicar color verde
        self.textbuffer.insert_with_tags_by_name(end_iter, texto, "console")

        # Auto-scroll al final
        end_iter = self.textbuffer.get_end_iter()
        mark = self.textbuffer.create_mark(None, end_iter, False)
        self.textview.scroll_to_mark(mark, 0.0, False, 0.0, 0.0)
        return False

    def actualizar_semaforo(self, estado):
        """Actualiza el semáforo según el estado de la conexión
        Estados: 'conectado', 'desconectado', 'conectando', 'desconectando'
        """
        if estado == 'conectado':
            icon_path = os.path.join(os.path.dirname(__file__), "icons", "green.fw.png")
            self.semaforo_image.set_from_file(icon_path)
        elif estado in ['conectando', 'desconectando']:
            icon_path = os.path.join(os.path.dirname(__file__), "icons", "yellow.fw.png")
            self.semaforo_image.set_from_file(icon_path)
        else:  # desconectado
            icon_path = os.path.join(os.path.dirname(__file__), "icons", "red.fw.png")
            self.semaforo_image.set_from_file(icon_path)
        return False

    def reactivar_botones(self):
        # Estado: Desconectado - Cambiar botón a "Conectar"
        self.boton_conectar_desconectar.set_sensitive(True)
        self.boton_conectar_desconectar.set_label(self.t('btn_connect'))
        self.conectado = False
        self.actualizar_semaforo('desconectado')
        return False

    def on_manual_clicked(self, widget):
        """Muestra el manual de usuario"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=self.t('help_manual')
        )

        manual_content = {
            'es': '''VPN Linux Desktop Connector - Manual de Usuario

1. CONFIGURACIÓN INICIAL:
   • Seleccione su archivo OVPN proporcionado por su administrador
   • Ingrese su usuario y contraseña
   • Las credenciales se guardan encriptadas localmente

2. CONEXIÓN:
   • Presione "Conectar VPN" para iniciar la conexión
   • Espere a ver el mensaje "Conectado ✓"
   • Los logs mostrarán el progreso de la conexión

3. DESCONEXIÓN:
   • Presione "Desconectar VPN" para terminar la conexión
   • Espere a que el proceso termine correctamente

4. IDIOMAS:
   • Use Configuración → Idioma para cambiar el idioma
   • La aplicación soporta 7 idiomas

5. SOLUCIÓN DE PROBLEMAS:
   • Verifique que el archivo OVPN sea válido
   • Confirme sus credenciales
   • Revise su conexión a internet
   • Consulte los logs para detalles del error''',
            'en': '''VPN Linux Desktop Connector - User Manual

1. INITIAL SETUP:
   • Select your OVPN file provided by your administrator
   • Enter your username and password
   • Credentials are saved encrypted locally

2. CONNECTION:
   • Press "Connect VPN" to start the connection
   • Wait to see the "Connected ✓" message
   • Logs will show connection progress

3. DISCONNECTION:
   • Press "Disconnect VPN" to end the connection
   • Wait for the process to terminate correctly

4. LANGUAGES:
   • Use Settings → Language to change language
   • The application supports 7 languages

5. TROUBLESHOOTING:
   • Verify that the OVPN file is valid
   • Confirm your credentials
   • Check your internet connection
   • Review logs for error details''',
            'zh': '''VPN Linux Desktop Connector - 用户手册

1. 初始设置：
   • 选择管理员提供的 OVPN 文件
   • 输入您的用户名和密码
   • 凭据将以加密方式保存在本地

2. 连接：
   • 按"连接 VPN"开始连接
   • 等待看到"已连接 ✓"消息
   • 日志将显示连接进度

3. 断开连接：
   • 按"断开 VPN"结束连接
   • 等待进程正确终止

4. 语言：
   • 使用配置 → 语言更改语言
   • 应用程序支持 7 种语言

5. 故障排除：
   • 验证 OVPN 文件是否有效
   • 确认您的凭据
   • 检查您的互联网连接
   • 查看日志了解错误详情''',
            'pt': '''VPN Linux Desktop Connector - Manual do Usuário

1. CONFIGURAÇÃO INICIAL:
   • Selecione seu arquivo OVPN fornecido pelo administrador
   • Digite seu usuário e senha
   • As credenciais são salvas criptografadas localmente

2. CONEXÃO:
   • Pressione "Conectar VPN" para iniciar a conexão
   • Aguarde ver a mensagem "Conectado ✓"
   • Os logs mostrarão o progresso da conexão

3. DESCONEXÃO:
   • Pressione "Desconectar VPN" para encerrar a conexão
   • Aguarde o processo terminar corretamente

4. IDIOMAS:
   • Use Configuração → Idioma para mudar o idioma
   • O aplicativo suporta 7 idiomas

5. SOLUÇÃO DE PROBLEMAS:
   • Verifique se o arquivo OVPN é válido
   • Confirme suas credenciais
   • Revise sua conexão com a internet
   • Consulte os logs para detalhes do erro''',
            'fr': '''VPN Linux Desktop Connector - Manuel d'Utilisateur

1. CONFIGURATION INITIALE:
   • Sélectionnez votre fichier OVPN fourni par votre administrateur
   • Entrez votre utilisateur et mot de passe
   • Les informations sont sauvegardées cryptées localement

2. CONNEXION:
   • Appuyez sur "Connecter VPN" pour démarrer la connexion
   • Attendez de voir le message "Connecté ✓"
   • Les journaux afficheront la progression de la connexion

3. DÉCONNEXION:
   • Appuyez sur "Déconnecter VPN" pour terminer la connexion
   • Attendez que le processus se termine correctement

4. LANGUES:
   • Utilisez Configuration → Langue pour changer la langue
   • L'application supporte 7 langues

5. DÉPANNAGE:
   • Vérifiez que le fichier OVPN est valide
   • Confirmez vos informations
   • Vérifiez votre connexion Internet
   • Consultez les journaux pour les détails d'erreur''',
            'de': '''VPN Linux Desktop Connector - Benutzerhandbuch

1. ERSTEINRICHTUNG:
   • Wählen Sie Ihre OVPN-Datei von Ihrem Administrator
   • Geben Sie Benutzer und Passwort ein
   • Anmeldedaten werden verschlüsselt lokal gespeichert

2. VERBINDUNG:
   • Drücken Sie "VPN verbinden" um die Verbindung zu starten
   • Warten Sie auf die Nachricht "Verbunden ✓"
   • Protokolle zeigen den Verbindungsfortschritt

3. TRENNUNG:
   • Drücken Sie "VPN trennen" um die Verbindung zu beenden
   • Warten Sie, bis der Prozess korrekt beendet ist

4. SPRACHEN:
   • Verwenden Sie Konfiguration → Sprache zum Ändern
   • Die Anwendung unterstützt 7 Sprachen

5. FEHLERBEHEBUNG:
   • Überprüfen Sie, dass die OVPN-Datei gültig ist
   • Bestätigen Sie Ihre Anmeldedaten
   • Überprüfen Sie Ihre Internetverbindung
   • Konsultieren Sie die Protokolle für Fehlerdetails''',
            'ja': '''VPN Linux Desktop Connector - ユーザーマニュアル

1. 初期設定：
   • 管理者から提供されたOVPNファイルを選択
   • ユーザー名とパスワードを入力
   • 認証情報は暗号化してローカルに保存されます

2. 接続：
   • "VPN接続"を押して接続を開始
   • "接続済み ✓"メッセージが表示されるまで待機
   • ログに接続の進行状況が表示されます

3. 切断：
   • "VPN切断"を押して接続を終了
   • プロセスが正常に終了するまで待機

4. 言語：
   • 設定 → 言語で言語を変更
   • アプリケーションは7つの言語をサポート

5. トラブルシューティング：
   • OVPNファイルが有効であることを確認
   • 認証情報を確認
   • インターネット接続を確認
   • エラーの詳細についてはログを確認'''
        }

        dialog.format_secondary_text(manual_content.get(self.idioma_actual, manual_content['es']))
        dialog.run()
        dialog.destroy()

    def on_report_bug_clicked(self, widget):
        """Abre opciones para reportar un bug"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text=self.t('help_report_bug')
        )

        report_text = {
            'es': '''Para reportar un error, por favor:

1. Incluya los logs de la aplicación
2. Describa los pasos para reproducir el error
3. Indique su versión de sistema operativo
4. Especifique la versión de OpenVPN instalada

Puede enviar el reporte a través de:
• GitHub Issues (recomendado)
• Email al equipo de desarrollo
• Sistema de tickets de su organización

Los logs se muestran en la ventana principal de la aplicación.''',
            'en': '''To report a bug, please:

1. Include the application logs
2. Describe the steps to reproduce the error
3. Indicate your operating system version
4. Specify the installed OpenVPN version

You can submit the report through:
• GitHub Issues (recommended)
• Email to the development team
• Your organization's ticket system

Logs are shown in the main application window.''',
            'zh': '''要报告错误，请：

1. 包含应用程序日志
2. 描述重现错误的步骤
3. 指出您的操作系统版本
4. 指定已安装的 OpenVPN 版本

您可以通过以下方式提交报告：
• GitHub Issues（推荐）
• 发送电子邮件给开发团队
• 您组织的工单系统

日志显示在应用程序主窗口中。''',
            'pt': '''Para reportar um erro, por favor:

1. Inclua os logs do aplicativo
2. Descreva os passos para reproduzir o erro
3. Indique sua versão do sistema operacional
4. Especifique a versão do OpenVPN instalada

Você pode enviar o relatório através de:
• GitHub Issues (recomendado)
• Email para a equipe de desenvolvimento
• Sistema de tickets da sua organização

Os logs são mostrados na janela principal do aplicativo.''',
            'fr': '''Pour signaler un bug, veuillez:

1. Inclure les journaux de l'application
2. Décrire les étapes pour reproduire l'erreur
3. Indiquer votre version du système d'exploitation
4. Spécifier la version d'OpenVPN installée

Vous pouvez soumettre le rapport via:
• GitHub Issues (recommandé)
• Email à l'équipe de développement
• Système de tickets de votre organisation

Les journaux sont affichés dans la fenêtre principale.''',
            'de': '''Um einen Fehler zu melden, bitte:

1. Fügen Sie die Anwendungsprotokolle hinzu
2. Beschreiben Sie die Schritte zum Reproduzieren
3. Geben Sie Ihre Betriebssystemversion an
4. Geben Sie die installierte OpenVPN-Version an

Sie können den Bericht einreichen über:
• GitHub Issues (empfohlen)
• E-Mail an das Entwicklungsteam
• Ticketsystem Ihrer Organisation

Protokolle werden im Hauptfenster angezeigt.''',
            'ja': '''バグを報告するには：

1. アプリケーションログを含める
2. エラーを再現する手順を説明
3. オペレーティングシステムのバージョンを示す
4. インストールされているOpenVPNバージョンを指定

レポートは以下を通じて送信できます：
• GitHub Issues（推奨）
• 開発チームへのメール
• 組織のチケットシステム

ログはアプリケーションのメインウィンドウに表示されます。'''
        }

        dialog.format_secondary_text(report_text.get(self.idioma_actual, report_text['es']))
        dialog.run()
        dialog.destroy()

    def on_donate_clicked(self, widget):
        """Muestra información para hacer donaciones"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text=self.t('help_donate')
        )

        donate_text = {
            'es': '''¡Gracias por considerar apoyar este proyecto!

VPN Linux Desktop Connector es un proyecto de código abierto gratuito. Su apoyo ayuda a:

• Mantener y mejorar la aplicación
• Agregar nuevas funcionalidades
• Proporcionar soporte técnico
• Mantener la documentación actualizada

Si desea hacer una donación, puede contactar al equipo de desarrollo para obtener información sobre las opciones disponibles.

Su apoyo es muy apreciado, ¡gracias!''',
            'en': '''Thank you for considering supporting this project!

VPN Linux Desktop Connector is a free open-source project. Your support helps to:

• Maintain and improve the application
• Add new features
• Provide technical support
• Keep documentation up to date

If you wish to make a donation, you can contact the development team for information about available options.

Your support is greatly appreciated, thank you!''',
            'zh': '''感谢您考虑支持这个项目！

VPN Linux Desktop Connector 是一个免费的开源项目。您的支持有助于：

• 维护和改进应用程序
• 添加新功能
• 提供技术支持
• 保持文档更新

如果您想捐赠，可以联系开发团队了解可用选项的信息。

非常感谢您的支持！''',
            'pt': '''Obrigado por considerar apoiar este projeto!

VPN Linux Desktop Connector é um projeto de código aberto gratuito. Seu apoio ajuda a:

• Manter e melhorar o aplicativo
• Adicionar novas funcionalidades
• Fornecer suporte técnico
• Manter a documentação atualizada

Se desejar fazer uma doação, pode contactar a equipe de desenvolvimento para obter informação sobre as opções disponíveis.

Seu apoio é muito apreciado, obrigado!''',
            'fr': '''Merci d'envisager de soutenir ce projet!

VPN Linux Desktop Connector est un projet open-source gratuit. Votre soutien aide à:

• Maintenir et améliorer l'application
• Ajouter de nouvelles fonctionnalités
• Fournir un support technique
• Maintenir la documentation à jour

Si vous souhaitez faire un don, vous pouvez contacter l'équipe de développement pour des informations sur les options disponibles.

Votre soutien est grandement apprécié, merci!''',
            'de': '''Vielen Dank, dass Sie erwägen, dieses Projekt zu unterstützen!

VPN Linux Desktop Connector ist ein kostenloses Open-Source-Projekt. Ihre Unterstützung hilft:

• Die Anwendung zu warten und zu verbessern
• Neue Funktionen hinzuzufügen
• Technischen Support bereitzustellen
• Die Dokumentation aktuell zu halten

Wenn Sie spenden möchten, können Sie das Entwicklungsteam für Informationen über verfügbare Optionen kontaktieren.

Ihre Unterstützung wird sehr geschätzt, vielen Dank!''',
            'ja': '''このプロジェクトのサポートをご検討いただきありがとうございます！

VPN Linux Desktop Connector は無料のオープンソースプロジェクトです。あなたのサポートは以下に役立ちます：

• アプリケーションの維持と改善
• 新機能の追加
• 技術サポートの提供
• ドキュメントの最新化

寄付をご希望の場合は、利用可能なオプションについて開発チームにお問い合わせください。

あなたのサポートに感謝します！'''
        }

        dialog.format_secondary_text(donate_text.get(self.idioma_actual, donate_text['es']))
        dialog.run()
        dialog.destroy()

    def on_about_clicked(self, widget):
        """Muestra el diálogo 'Acerca de'"""
        about_dialog = Gtk.AboutDialog(transient_for=self, modal=True)
        about_dialog.set_program_name("VPN Linux Desktop Connector")
        about_dialog.set_version("1.0.0")
        about_dialog.set_copyright("© 2025")

        about_text = {
            'es': "Una aplicación de escritorio para gestionar conexiones VPN en Linux usando OpenVPN.",
            'en': "A desktop application to manage VPN connections on Linux using OpenVPN.",
            'zh': "使用 OpenVPN 在 Linux 上管理 VPN 连接的桌面应用程序。",
            'pt': "Uma aplicação de desktop para gerenciar conexões VPN no Linux usando OpenVPN.",
            'fr': "Une application de bureau pour gérer les connexions VPN sur Linux avec OpenVPN.",
            'de': "Eine Desktop-Anwendung zur Verwaltung von VPN-Verbindungen unter Linux mit OpenVPN.",
            'ja': "OpenVPN を使用して Linux で VPN 接続を管理するデスクトップアプリケーション。"
        }

        about_dialog.set_comments(about_text.get(self.idioma_actual, about_text['es']))
        about_dialog.set_website("https://github.com/danielrincon302/VPN-Linux-Desktop-Connector")
        about_dialog.set_website_label("GitHub")
        about_dialog.set_license("GPL 3.0")

        # Autores del proyecto - Se mostrarán en la pestaña "Créditos" sin el encabezado "Creado por"
        authors = [
            "Desarrollado por:",
            "Urreste García, L. A.\t\tDiseñador UX\t📧  antoniourresty93@gmail.com",
            "Capote Casas, F. E.\t\tIngeniero\t\t📧  fabianesteban1991@gmail.com",
            "Castellanos Muriel, J. A.\tIngeniero\t\t📧  jaime.castellanos14@gmail.com",
            "Rincón Brito, C. D.\t\tIngeniero\t\t📧  daniel@onfraga.com"
        ]
        about_dialog.add_credit_section("", authors)

        # Logo de la aplicación
        try:
            from gi.repository import GdkPixbuf
            icon_path = os.path.join(os.path.dirname(__file__), "icons", "VPN-LDC_32x32.svg")
            if os.path.exists(icon_path):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 128, 128, True)
                about_dialog.set_logo(pixbuf)
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")

        about_dialog.run()
        about_dialog.destroy()

    def crear_status_icon(self):
        """Crea el ícono de bandeja del sistema usando Gtk.StatusIcon"""
        # Crear el StatusIcon
        self.status_icon = Gtk.StatusIcon()

        # Intentar cargar el ícono personalizado
        icon_path = os.path.join(os.path.dirname(__file__), "icons", "VPN-LDC_24x24.svg")
        if os.path.exists(icon_path):
            try:
                self.status_icon.set_from_file(icon_path)
            except Exception as e:
                print(f"No se pudo cargar el ícono de bandeja: {e}")
                self.status_icon.set_from_icon_name("network-vpn")
        else:
            # Usar ícono del sistema si no se encuentra el personalizado
            self.status_icon.set_from_icon_name("network-vpn")

        self.status_icon.set_tooltip_text("VPN Linux Desktop Connector")

        # Conectar eventos
        self.status_icon.connect("popup-menu", self.on_status_icon_popup)
        self.status_icon.connect("activate", self.on_status_icon_activate)

        # Hacer visible el ícono
        self.status_icon.set_visible(True)

        # Crear el menú del status icon
        self.crear_menu_status_icon()

    def crear_menu_status_icon(self):
        """Crea el menú del status icon"""
        self.status_menu = Gtk.Menu()

        # Opción: Abrir
        self.menu_si_abrir = Gtk.MenuItem()
        abrir_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        abrir_icon = Gtk.Image.new_from_icon_name('document-open', Gtk.IconSize.MENU)
        abrir_label = Gtk.Label(label="Abrir")
        abrir_label.set_xalign(0)
        abrir_box.pack_start(abrir_icon, False, False, 0)
        abrir_box.pack_start(abrir_label, True, True, 0)
        self.menu_si_abrir.add(abrir_box)
        self.menu_si_abrir.connect("activate", self.on_status_icon_abrir)
        self.status_menu.append(self.menu_si_abrir)

        # Separador
        self.status_menu.append(Gtk.SeparatorMenuItem())

        # Estado
        self.menu_si_estado = Gtk.MenuItem()
        estado_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.menu_si_estado_icon = Gtk.Image.new_from_icon_name('dialog-error', Gtk.IconSize.MENU)  # Rojo para desconectado
        self.menu_si_estado_label = Gtk.Label(label="Estado: Desconectado")
        self.menu_si_estado_label.set_xalign(0)
        estado_box.pack_start(self.menu_si_estado_icon, False, False, 0)
        estado_box.pack_start(self.menu_si_estado_label, True, True, 0)
        self.menu_si_estado.add(estado_box)
        self.menu_si_estado.set_sensitive(False)
        self.status_menu.append(self.menu_si_estado)

        # IP VPN
        self.menu_si_ip_vpn = Gtk.MenuItem()
        ip_vpn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        ip_vpn_icon = Gtk.Image.new_from_icon_name('changes-prevent', Gtk.IconSize.MENU)
        self.menu_si_ip_vpn_label = Gtk.Label(label="IP VPN: No conectado")
        self.menu_si_ip_vpn_label.set_xalign(0)
        ip_vpn_box.pack_start(ip_vpn_icon, False, False, 0)
        ip_vpn_box.pack_start(self.menu_si_ip_vpn_label, True, True, 0)
        self.menu_si_ip_vpn.add(ip_vpn_box)
        self.menu_si_ip_vpn.set_sensitive(False)
        self.status_menu.append(self.menu_si_ip_vpn)

        # IP Local
        self.menu_si_ip_local = Gtk.MenuItem()
        ip_local_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        ip_local_icon = Gtk.Image.new_from_icon_name('network-wired', Gtk.IconSize.MENU)
        self.menu_si_ip_local_label = Gtk.Label(label="IP Local: Cargando...")
        self.menu_si_ip_local_label.set_xalign(0)
        ip_local_box.pack_start(ip_local_icon, False, False, 0)
        ip_local_box.pack_start(self.menu_si_ip_local_label, True, True, 0)
        self.menu_si_ip_local.add(ip_local_box)
        self.menu_si_ip_local.set_sensitive(False)
        self.status_menu.append(self.menu_si_ip_local)

        # IP Pública
        self.menu_si_ip_publica = Gtk.MenuItem()
        ip_publica_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        ip_publica_icon = Gtk.Image.new_from_icon_name('network-transmit-receive', Gtk.IconSize.MENU)
        self.menu_si_ip_publica_label = Gtk.Label(label="IP Pública: Cargando...")
        self.menu_si_ip_publica_label.set_xalign(0)
        ip_publica_box.pack_start(ip_publica_icon, False, False, 0)
        ip_publica_box.pack_start(self.menu_si_ip_publica_label, True, True, 0)
        self.menu_si_ip_publica.add(ip_publica_box)
        self.menu_si_ip_publica.set_sensitive(False)
        self.status_menu.append(self.menu_si_ip_publica)

        # Tipo de conexión
        self.menu_si_conexion = Gtk.MenuItem()
        conexion_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.menu_si_conexion_icon = Gtk.Image.new_from_icon_name('network-wired', Gtk.IconSize.MENU)  # Por defecto cableada
        self.menu_si_conexion_label = Gtk.Label(label="Conexión: Cargando...")
        self.menu_si_conexion_label.set_xalign(0)
        conexion_box.pack_start(self.menu_si_conexion_icon, False, False, 0)
        conexion_box.pack_start(self.menu_si_conexion_label, True, True, 0)
        self.menu_si_conexion.add(conexion_box)
        self.menu_si_conexion.set_sensitive(False)
        self.status_menu.append(self.menu_si_conexion)

        # Separador
        self.status_menu.append(Gtk.SeparatorMenuItem())

        # Opción: Salir
        menu_si_salir = Gtk.MenuItem()
        salir_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        salir_icon = Gtk.Image.new_from_icon_name('application-exit', Gtk.IconSize.MENU)
        salir_label = Gtk.Label(label="Salir")
        salir_label.set_xalign(0)
        salir_box.pack_start(salir_icon, False, False, 0)
        salir_box.pack_start(salir_label, True, True, 0)
        menu_si_salir.add(salir_box)
        menu_si_salir.connect("activate", self.on_status_icon_salir)
        self.status_menu.append(menu_si_salir)

        self.status_menu.show_all()

    def actualizar_menu_status_icon(self):
        """Actualiza la información en el menú del status icon"""
        # Ejecutar en un hilo para no bloquear la UI
        def actualizar():
            # Obtener ruta del ícono
            icon_path = os.path.join(os.path.dirname(__file__), "icons", "VPN-LDC_24x24.svg")

            # Obtener estado VPN
            if self.proceso and self.proceso.poll() is None:
                estado = "Conectado"
                GLib.idle_add(self.menu_si_estado_label.set_text, f"Estado: {estado} ✓")
                # Cambiar ícono a verde (conectado)
                GLib.idle_add(self.menu_si_estado_icon.set_from_icon_name, "emblem-default", Gtk.IconSize.MENU)
                # Mantener el mismo ícono pero con tooltip actualizado
                if os.path.exists(icon_path):
                    GLib.idle_add(self.status_icon.set_tooltip_text, "VPN Linux Desktop Connector - Conectado ✓")
                else:
                    GLib.idle_add(self.status_icon.set_from_icon_name, "network-vpn-symbolic")
            else:
                estado = "Desconectado"
                GLib.idle_add(self.menu_si_estado_label.set_text, f"Estado: {estado}")
                # Cambiar ícono a rojo (desconectado)
                GLib.idle_add(self.menu_si_estado_icon.set_from_icon_name, "dialog-error", Gtk.IconSize.MENU)
                # Mantener el ícono pero actualizar tooltip
                if os.path.exists(icon_path):
                    GLib.idle_add(self.status_icon.set_tooltip_text, "VPN Linux Desktop Connector - Desconectado")
                else:
                    GLib.idle_add(self.status_icon.set_from_icon_name, "network-vpn")

            # Obtener IPs
            ip_vpn = obtener_ip_vpn()
            ip_local = obtener_ip_local()
            ip_publica = obtener_ip_publica()
            tipo_conexion = obtener_tipo_conexion()

            # Actualizar menú en el hilo principal
            GLib.idle_add(self.menu_si_ip_vpn_label.set_text, f"IP VPN: {ip_vpn}")
            GLib.idle_add(self.menu_si_ip_local_label.set_text, f"IP Local: {ip_local}")
            GLib.idle_add(self.menu_si_ip_publica_label.set_text, f"IP Pública: {ip_publica}")
            GLib.idle_add(self.menu_si_conexion_label.set_text, f"Conexión: {tipo_conexion}")

            # Cambiar ícono según el tipo de conexión
            if "Wi-Fi" in tipo_conexion or "WiFi" in tipo_conexion or "inalámbrica" in tipo_conexion.lower():
                GLib.idle_add(self.menu_si_conexion_icon.set_from_icon_name, "network-wireless", Gtk.IconSize.MENU)
            else:
                GLib.idle_add(self.menu_si_conexion_icon.set_from_icon_name, "network-wired", Gtk.IconSize.MENU)

        thread = threading.Thread(target=actualizar, daemon=True)
        thread.start()

        return True  # Continuar ejecutando el timeout

    def on_status_icon_popup(self, icon, button, time):
        """Muestra el menú popup del status icon"""
        self.status_menu.popup(None, None, None, None, button, time)

    def on_status_icon_activate(self, icon):
        """Maneja el clic izquierdo en el status icon"""
        if self.get_visible():
            self.hide()
        else:
            self.show_all()
            self.present()

    def on_ventana_cerrar(self, widget, event):
        """Maneja el evento de cerrar la ventana"""
        # Minimizar a la bandeja en lugar de cerrar
        self.hide()
        return True  # Prevenir el cierre

    def on_status_icon_abrir(self, widget):
        """Abre/muestra la ventana desde el status icon"""
        self.show_all()
        self.present()

    def on_status_icon_salir(self, widget):
        """Cierra completamente la aplicación"""
        # Desconectar VPN si está conectada
        if self.proceso and self.proceso.poll() is None:
            try:
                self.proceso.send_signal(signal.SIGINT)
                self.proceso.wait(timeout=3)
            except:
                pass

        # Detener el temporizador de anti-suspensión si está activo
        self.detener_anti_suspend()

        Gtk.main_quit()

def main():
    ventana = VentanaVPN()
    ventana.connect("destroy", Gtk.main_quit)
    ventana.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
