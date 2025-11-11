  cd ~ && curl -L https://github.com/danielrincon302/VPN-Linux-Desktop-Connector/archive/refs/heads/main.zip -o vpn-temp.zip && 
  unzip -o -q vpn-temp.zip && rm -rf VPN-Desktop-Linux-Conector 2>/dev/null && 
  mv VPN-Linux-Desktop-Connector-main VPN-Desktop-Linux-Conector && 
  rm vpn-temp.zip && cp ~/VPN-Desktop-Linux-Conector/Run-VPN-Desktop-Linux-Conector.desktop "$(xdg-user-dir DESKTOP)"/ && 
  chmod +x "$(xdg-user-dir DESKTOP)/Run-VPN-Desktop-Linux-Conector.desktop"  && 
  sed -i "s|\$HOME|$HOME|g" "$(xdg-user-dir DESKTOP)/Run-VPN-Desktop-Linux-Conector.desktop"  && 
  chmod +x "$(xdg-user-dir DESKTOP)/Run-VPN-Desktop-Linux-Conector.desktop" && 
  gio set "$(xdg-user-dir DESKTOP)/Run-VPN-Desktop-Linux-Conector.desktop" metadata::trusted true
  echo "✓ Installation complete. Check your desktop icon"