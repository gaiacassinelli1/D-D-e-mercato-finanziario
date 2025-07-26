"""
D&D Market Analysis Visualizer - Fixed & Extended
================================================

Visualizzatore specializzato per i dati del market_simulator.py
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DNDMarketVisualizerFixed:
    
    def __init__(self, data_dir="market_data"):
        self.data_dir = data_dir
        self.output_dir = "site/market_images"
        self.ensure_output_dirs()
        
        # Dati caricati dai file JSON del simulator
        self.stocks_data = {}
        self.market_report = {}
        self.market_summary = {}
        
        # Setup styling pastello
        self.setup_pastel_styling()
        
        # Carica i dati
        self.load_market_data()

    def setup_pastel_styling(self):
        """Setup styling con colori pastello più visibili e sfondo bianco"""
        plt.style.use('default')
        sns.set_style("whitegrid")
        
        # Palette colori pastello
        self.color_palettes = {
            'soft_pastels': ['#FFB3D9', '#B3D9FF', '#B3FFB3', '#FFD9B3', '#D9B3FF', '#B3FFFF', '#FFB3B3', '#D9FFB3'],
            'pastel_blues': ['#E1F0FF', '#CCE7FF', '#B8DEFF', '#A3D5FF', '#8FCCFF', '#7AC3FF', '#66BAFF', '#52B1FF'],
            'pastel_greens': ['#E1FFE1', '#CCFFCC', '#B8FFB8', '#A3FFA3', '#8FFF8F', '#7AFF7A', '#66FF66', '#52FF52'],
            'pastel_pinks': ['#FFE1F0', '#FFCCE6', '#FFB8DD', '#FFA3D3', '#FF8FCA', '#FF7AC0', '#FF66B7', '#FF52AD'],
            'pastel_purples': ['#F0E1FF', '#E6CCFF', '#DDB8FF', '#D3A3FF', '#CA8FFF', '#C07AFF', '#B766FF', '#AD52FF'],
            'pastel_oranges': ['#FFF0E1', '#FFE6CC', '#FFDDB8', '#FFD3A3', '#FFCA8F', '#FFC07A', '#FFB766', '#FFAD52'],
            'warm_pastels': ['#FFD166', '#F4A261', '#E76F51', '#E63946', '#457B9D', '#1D3557', '#52B788', '#40E0D0'],
            'cool_pastels': ['#81C784', '#A5D6A7', '#C8E6C9', '#81D4FA', '#B3E5FC', '#CE93D8', '#F48FB1', '#FFCC80']
        }
        
        # Parametri matplotlib per look pastello
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': '#D0D0D0',
            'axes.linewidth': 0.8,
            'axes.labelcolor': '#444444',
            'text.color': '#444444',
            'xtick.color': '#666666',
            'ytick.color': '#666666',
            'grid.color': '#E8E8E8',
            'grid.alpha': 0.7,
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 11,
            'legend.fontsize': 9,
            'figure.titlesize': 16,
            'font.family': 'sans-serif',
            'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans']
        })

    def ensure_output_dirs(self):
        """Crea le directory di output"""
        os.makedirs(self.output_dir, exist_ok=True)

    def load_market_data(self):
        """Carica i dati dai file JSON generati dal market simulator"""
        try:
            # Carica stocks dettagliati
            stocks_file = os.path.join(self.data_dir, 'financial_stocks.json')
            if os.path.exists(stocks_file):
                with open(stocks_file, 'r') as f:
                    self.stocks_data = json.load(f)
                print(f"✅ Loaded {len(self.stocks_data)} stocks from {stocks_file}")
            else:
                print(f"❌ File not found: {stocks_file}")
                return False
            
            # Carica market report
            report_file = os.path.join(self.data_dir, 'market_report.json')
            if os.path.exists(report_file):
                with open(report_file, 'r') as f:
                    self.market_report = json.load(f)
                print(f"✅ Loaded market report from {report_file}")
            
            # Carica market summary
            summary_file = os.path.join(self.data_dir, 'market_summary.json')
            if os.path.exists(summary_file):
                with open(summary_file, 'r') as f:
                    self.market_summary = json.load(f)
                print(f"✅ Loaded market summary from {summary_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading market data: {e}")
            return False

    def plot_1_pe_ratio_valuation_analysis(self):
        """1. Analisi P/E Ratio - Valutazione delle classi"""
        print("📊 1. Generating P/E Ratio Valuation Analysis...")
        
        if not self.stocks_data:
            print("No stock data available")
            return
        
        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor('white')
        
        # Prepara dati P/E
        pe_data = []
        for symbol, stock in self.stocks_data.items():
            if stock['pe_ratio'] > 0 and stock['pe_ratio'] < 100:  # Filtra outliers
                pe_data.append({
                    'name': stock['name'],
                    'symbol': symbol,
                    'pe_ratio': stock['pe_ratio'],
                    'current_price': stock['current_price'],
                    'market_cap': stock['market_cap'],
                    'dividend_yield': stock['dividend_yield']
                })
        
        if not pe_data:
            print("No valid P/E data")
            return
        
        df = pd.DataFrame(pe_data)
        df_sorted = df.sort_values('pe_ratio', ascending=False)
        
        # Grafico a barre orizzontali
        colors = self.color_palettes['pastel_blues'][:len(df_sorted)]
        bars = ax.barh(range(len(df_sorted)), df_sorted['pe_ratio'], 
                      color=colors, alpha=0.85, edgecolor='white', linewidth=2)
        
        # Etichette e styling
        ax.set_yticks(range(len(df_sorted)))
        ax.set_yticklabels(df_sorted['name'], fontsize=11)
        ax.set_xlabel('P/E Ratio', fontsize=12, fontweight='bold', color='#444444')
        ax.set_title('D&D Class Stock Valuation Analysis\nPrice-to-Earnings Ratio Comparison', 
                    fontsize=16, fontweight='bold', pad=20, color='#333333')
        
        # Linee di riferimento per valutazione
        ax.axvline(x=15, color='#4CAF50', linestyle='--', alpha=0.8, linewidth=2, label='Undervalued (<15)')
        ax.axvline(x=25, color='#FFC107', linestyle='--', alpha=0.8, linewidth=2, label='Fair Value (15-25)')
        ax.axvline(x=35, color='#FF5722', linestyle='--', alpha=0.8, linewidth=2, label='Overvalued (>35)')
        
        # Aggiungi etichette valori
        for i, (bar, pe) in enumerate(zip(bars, df_sorted['pe_ratio'])):
            ax.text(pe + 0.5, bar.get_y() + bar.get_height()/2, 
                   f'{pe:.1f}', va='center', fontweight='bold', fontsize=10, color='#444444')
        
        ax.grid(axis='x', alpha=0.5, color='#D0D0D0')
        ax.legend(loc='lower right', fontsize=10, frameon=True, fancybox=True)
        ax.set_facecolor('white')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "1_pe_ratio_valuation.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_2_dividend_yield_ranking(self):
        """2. Ranking Dividend Yield - Income investing"""
        print("📊 2. Generating Dividend Yield Ranking...")
        
        if not self.stocks_data:
            print("No stock data available")
            return
        
        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor('white')
        
        # Prepara dati dividendi
        dividend_data = []
        for symbol, stock in self.stocks_data.items():
            dividend_data.append({
                'name': stock['name'],
                'symbol': symbol,
                'dividend_yield': stock['dividend_yield'],
                'annual_dividends': stock['annual_dividends'],
                'current_price': stock['current_price']
            })
        
        df = pd.DataFrame(dividend_data)
        df_sorted = df.sort_values('dividend_yield', ascending=True)  # Ordinamento per le barre orizzontali
        
        # Colori gradient pastello basati su yield più visibili
        colors = []
        max_yield = df_sorted['dividend_yield'].max()
        for yield_val in df_sorted['dividend_yield']:
            intensity = yield_val / max_yield
            if intensity < 0.33:
                colors.append('#FFB3B3')  # Rosso pastello per yield bassi
            elif intensity < 0.66:
                colors.append('#FFD9B3')  # Arancione pastello per yield medi
            else:
                colors.append('#B3FFB3')  # Verde pastello per yield alti
        
        bars = ax.barh(range(len(df_sorted)), df_sorted['dividend_yield'], 
                      color=colors, alpha=0.85, edgecolor='white', linewidth=2)
        
        # Styling
        ax.set_yticks(range(len(df_sorted)))
        ax.set_yticklabels(df_sorted['name'], fontsize=11)
        ax.set_xlabel('Dividend Yield (%)', fontsize=12, fontweight='bold', color='#444444')
        ax.set_title('D&D Class Stock Dividend Analysis\nIncome Investment Opportunities', 
                    fontsize=16, fontweight='bold', pad=20, color='#333333')
        
        # Aggiungi etichette valori e dividend annuali
        for i, (bar, yield_val, annual_div) in enumerate(zip(bars, df_sorted['dividend_yield'], df_sorted['annual_dividends'])):
            ax.text(yield_val + 0.05, bar.get_y() + bar.get_height()/2, 
                   f'{yield_val:.2f}% (${annual_div:.2f})', va='center', 
                   fontweight='bold', fontsize=9, color='#444444')
        
        # Linea di riferimento per "good dividend yield"
        ax.axvline(x=3.0, color='#2196F3', linestyle='--', alpha=0.8, linewidth=2, 
                  label='Good Dividend Yield (3%+)')
        
        ax.grid(axis='x', alpha=0.5, color='#D0D0D0')
        ax.legend(loc='lower right', fontsize=10, frameon=True)
        ax.set_facecolor('white')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "2_dividend_yield_ranking.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_3_market_cap_visualization(self):
        """3. Visualizzazione Market Cap - Dimensioni aziende"""
        print("📊 3. Generating Market Cap Visualization...")
        
        if not self.stocks_data:
            print("No stock data available")
            return
        
        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor('white')
        
        # Prepara dati market cap
        cap_data = []
        for symbol, stock in self.stocks_data.items():
            cap_data.append({
                'name': stock['name'],
                'symbol': symbol,
                'market_cap': stock['market_cap'],
                'current_price': stock['current_price'],
                'outstanding_shares': stock['outstanding_shares']
            })
        
        df = pd.DataFrame(cap_data)
        df_sorted = df.sort_values('market_cap', ascending=False)
        
        # Market cap in milioni per leggibilità
        market_caps_millions = [cap / 1e6 for cap in df_sorted['market_cap']]
        
        # Colori pastello gradient basati su dimensione
        colors = self.color_palettes['pastel_greens'][:len(df_sorted)]
        
        bars = ax.bar(range(len(df_sorted)), market_caps_millions, 
                     color=colors, alpha=0.85, edgecolor='white', linewidth=2)
        
        # Styling
        ax.set_xticks(range(len(df_sorted)))
        ax.set_xticklabels(df_sorted['name'], rotation=45, ha='right', fontsize=11)
        ax.set_ylabel('Market Capitalization ($ Millions)', fontsize=12, fontweight='bold', color='#444444')
        ax.set_title('D&D Class Stock Market Capitalization\nCompany Size Comparison', 
                    fontsize=16, fontweight='bold', pad=20, color='#333333')
        
        # Aggiungi etichette valori
        for bar, cap_mil in zip(bars, market_caps_millions):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + cap_mil*0.02,
                   f'${cap_mil:.0f}M', ha='center', fontweight='bold', fontsize=9, color='#444444')
        
        # Categorie market cap
        ax.axhline(y=500, color='#FF9800', linestyle='--', alpha=0.8, 
                  label='Mid Cap ($500M+)', linewidth=2)
        ax.axhline(y=1000, color='#4CAF50', linestyle='--', alpha=0.8, 
                  label='Large Cap ($1B+)', linewidth=2)
        
        ax.grid(axis='y', alpha=0.5, color='#D0D0D0')
        ax.legend(loc='upper right', fontsize=10, frameon=True)
        ax.set_facecolor('white')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "3_market_cap_visualization.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_4_beta_risk_assessment(self):
        """4. Analisi Beta - Risk assessment"""
        print("📊 4. Generating Beta Risk Assessment...")
        
        if not self.stocks_data:
            print("No stock data available")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        fig.patch.set_facecolor('white')
        
        # Prepara dati beta
        beta_data = []
        for symbol, stock in self.stocks_data.items():
            beta_data.append({
                'name': stock['name'],
                'symbol': symbol,
                'beta': stock['beta'],
                'current_price': stock['current_price'],
                'daily_change_percent': stock['daily_change_percent']
            })
        
        df = pd.DataFrame(beta_data)
        df_sorted = df.sort_values('beta', ascending=False)
        
        # Plot 1: Beta ranking
        colors1 = []
        for beta in df_sorted['beta']:
            if beta < 0.8:
                colors1.append('#B3FFB3')  # Verde pastello - Low risk
            elif beta <= 1.2:
                colors1.append('#FFD9B3')  # Giallo pastello - Market risk
            else:
                colors1.append('#FFB3B3')  # Rosa pastello - High risk
        
        bars1 = ax1.barh(range(len(df_sorted)), df_sorted['beta'], 
                        color=colors1, alpha=0.85, edgecolor='white', linewidth=2)
        
        ax1.set_yticks(range(len(df_sorted)))
        ax1.set_yticklabels(df_sorted['name'], fontsize=11)
        ax1.set_xlabel('Beta (Risk Level)', fontsize=12, fontweight='bold', color='#444444')
        ax1.set_title('Beta Risk Assessment\nSystematic Risk by Class', 
                     fontsize=14, fontweight='bold', color='#333333')
        
        # Linee di riferimento
        ax1.axvline(x=0.8, color='#4CAF50', linestyle='--', alpha=0.8, label='Low Risk (<0.8)')
        ax1.axvline(x=1.0, color='#2196F3', linestyle='-', alpha=0.9, label='Market Risk (1.0)', linewidth=2)
        ax1.axvline(x=1.2, color='#FF5722', linestyle='--', alpha=0.8, label='High Risk (>1.2)')
        
        # Etichette valori
        for bar, beta in zip(bars1, df_sorted['beta']):
            ax1.text(beta + 0.02, bar.get_y() + bar.get_height()/2, 
                    f'{beta:.2f}', va='center', fontweight='bold', fontsize=10, color='#444444')
        
        ax1.grid(axis='x', alpha=0.5, color='#D0D0D0')
        ax1.legend(loc='lower right', fontsize=9)
        ax1.set_facecolor('white')
        
        # Plot 2: Beta vs Performance scatter
        scatter = ax2.scatter(df['beta'], df['daily_change_percent'], 
                            s=200, alpha=0.8, c='#D9B3FF',
                            edgecolors='white', linewidth=2)
        
        # Etichette per ogni punto
        for _, stock in df.iterrows():
            ax2.annotate(stock['name'][:8], (stock['beta'], stock['daily_change_percent']),
                        xytext=(8, 8), textcoords='offset points',
                        fontsize=9, fontweight='bold', color='#444444',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
        ax2.set_xlabel('Beta (Risk)', fontsize=12, fontweight='bold', color='#444444')
        ax2.set_ylabel('Daily Change (%)', fontsize=12, fontweight='bold', color='#444444')
        ax2.set_title('Risk vs Performance\nBeta vs Daily Returns', 
                     fontsize=14, fontweight='bold', color='#333333')
        
        # Linee di riferimento
        ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.6)
        ax2.axvline(x=1, color='gray', linestyle='-', alpha=0.6)
        
        ax2.grid(alpha=0.5, color='#D0D0D0')
        ax2.set_facecolor('white')
        
        plt.suptitle('D&D Class Beta Risk Analysis', fontsize=16, fontweight='bold', color='#333333')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "4_beta_risk_assessment.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_5_sector_performance_comparison(self):
        """5. Confronto Performance Settoriali - Caster vs Martial vs Hybrid"""
        print("📊 5. Generating Sector Performance Comparison...")
        
        if not self.stocks_data:
            print("No stock data available")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.patch.set_facecolor('white')
        
        # Classifica stocks per settore
        caster_classes = ['Wizard', 'Sorcerer', 'Warlock', 'Bard', 'Cleric', 'Druid']
        martial_classes = ['Fighter', 'Barbarian', 'Ranger', 'Paladin', 'Rogue', 'Monk']
        
        sector_data = []
        for symbol, stock in self.stocks_data.items():
            if stock['name'] in caster_classes:
                sector = 'Caster'
            elif stock['name'] in martial_classes:
                sector = 'Martial'
            else:
                sector = 'Hybrid'
            
            sector_data.append({
                'name': stock['name'],
                'sector': sector,
                'daily_change_percent': stock['daily_change_percent'],
                'market_cap': stock['market_cap'],
                'pe_ratio': stock['pe_ratio'],
                'dividend_yield': stock['dividend_yield']
            })
        
        df = pd.DataFrame(sector_data)
        
        # Colori settore 
        sector_colors = {
            'Caster': '#B3D9FF',    # Blu pastello
            'Martial': '#FFB3B3',   # Rosa pastello  
            'Hybrid': '#B3FFB3'     # Verde pastello
        }
        
        # Plot 1: Performance media per settore
        sector_performance = df.groupby('sector')['daily_change_percent'].mean()
        colors1 = [sector_colors[sector] for sector in sector_performance.index]
        
        bars1 = ax1.bar(sector_performance.index, sector_performance.values, 
                       color=colors1, alpha=0.85, edgecolor='white', linewidth=2)
        
        ax1.set_ylabel('Average Daily Change (%)', fontsize=11, fontweight='bold', color='#444444')
        ax1.set_title('Average Performance by Sector', fontsize=12, fontweight='bold', color='#333333')
        ax1.grid(axis='y', alpha=0.5, color='#D0D0D0')
        ax1.set_facecolor('white')
        
        # Etichette valori
        for bar, perf in zip(bars1, sector_performance.values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                    f'{perf:.2f}%', ha='center', fontweight='bold', fontsize=10, color='#444444')
        
        # Plot 2: Market cap per settore
        sector_mcap = df.groupby('sector')['market_cap'].sum() / 1e6  # In milioni
        colors2 = [sector_colors[sector] for sector in sector_mcap.index]
        
        bars2 = ax2.bar(sector_mcap.index, sector_mcap.values, 
                       color=colors2, alpha=0.85, edgecolor='white', linewidth=2)
        
        ax2.set_ylabel('Total Market Cap ($ Millions)', fontsize=11, fontweight='bold', color='#444444')
        ax2.set_title('Market Capitalization by Sector', fontsize=12, fontweight='bold', color='#333333')
        ax2.grid(axis='y', alpha=0.5, color='#D0D0D0')
        ax2.set_facecolor('white')
        
        # Etichette valori
        for bar, mcap in zip(bars2, sector_mcap.values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + mcap*0.02,
                    f'${mcap:.0f}M', ha='center', fontweight='bold', fontsize=10, color='#444444')
        
        # Plot 3: P/E medio per settore
        sector_pe = df.groupby('sector')['pe_ratio'].mean()
        colors3 = [sector_colors[sector] for sector in sector_pe.index]
        
        bars3 = ax3.bar(sector_pe.index, sector_pe.values, 
                       color=colors3, alpha=0.85, edgecolor='white', linewidth=2)
        
        ax3.set_ylabel('Average P/E Ratio', fontsize=11, fontweight='bold', color='#444444')
        ax3.set_title('Valuation by Sector', fontsize=12, fontweight='bold', color='#333333')
        ax3.grid(axis='y', alpha=0.5, color='#D0D0D0')
        ax3.set_facecolor('white')
        
        # Etichette valori
        for bar, pe in zip(bars3, sector_pe.values):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + pe*0.02,
                    f'{pe:.1f}', ha='center', fontweight='bold', fontsize=10, color='#444444')
        
        # Plot 4: Dividend yield medio per settore
        sector_div = df.groupby('sector')['dividend_yield'].mean()
        colors4 = [sector_colors[sector] for sector in sector_div.index]
        
        bars4 = ax4.bar(sector_div.index, sector_div.values, 
                       color=colors4, alpha=0.85, edgecolor='white', linewidth=2)
        
        ax4.set_ylabel('Average Dividend Yield (%)', fontsize=11, fontweight='bold', color='#444444')
        ax4.set_title('Income Generation by Sector', fontsize=12, fontweight='bold', color='#333333')
        ax4.grid(axis='y', alpha=0.5, color='#D0D0D0')
        ax4.set_facecolor('white')
        
        # Etichette valori
        for bar, div_yield in zip(bars4, sector_div.values):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + div_yield*0.02,
                    f'{div_yield:.2f}%', ha='center', fontweight='bold', fontsize=10, color='#444444')
        
        plt.suptitle('D&D Market Sector Analysis - Caster vs Martial vs Hybrid', 
                    fontsize=16, fontweight='bold', color='#333333', y=0.98)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "5_sector_performance_comparison.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_6_price_vs_performance_bubble(self):
        """6. Bubble Chart Prezzo vs Performance"""
        print("📊 6. Generating Price vs Performance Bubble Chart...")
        
        if not self.stocks_data:
            print("No stock data available")
            return
        
        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor('white')
        
        # Prepara dati per bubble chart
        bubble_data = []
        for symbol, stock in self.stocks_data.items():
            bubble_data.append({
                'name': stock['name'],
                'current_price': stock['current_price'],
                'daily_change_percent': stock['daily_change_percent'],
                'market_cap': stock['market_cap'],
                'volume': stock['volume'],
                'beta': stock['beta']
            })
        
        df = pd.DataFrame(bubble_data)
        
        # Dimensioni bubble basate su market cap
        sizes = [(cap / df['market_cap'].max()) * 1500 + 100 for cap in df['market_cap']]
        
        # Colori basati su beta (rischio)
        colors = []
        for beta in df['beta']:
            if beta < 0.8:
                colors.append('#81C784')  # Verde pastello - Low risk
            elif beta <= 1.2:
                colors.append('#FFCC80')  # Giallo pastello - Market risk
            else:
                colors.append('#F48FB1')  # Rosa pastello - High risk
        
        scatter = ax.scatter(df['current_price'], df['daily_change_percent'], 
                           s=sizes, c=colors, alpha=0.8, edgecolors='white',
                           linewidth=2)
        
        # Etichette per ogni bubble
        for _, stock in df.iterrows():
            ax.annotate(stock['name'][:8], (stock['current_price'], stock['daily_change_percent']),
                       xytext=(8, 8), textcoords='offset points',
                       fontsize=9, fontweight='bold', color='#444444',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
        ax.set_xlabel('Current Stock Price ($)', fontsize=12, fontweight='bold', color='#444444')
        ax.set_ylabel('Daily Change (%)', fontsize=12, fontweight='bold', color='#444444')
        ax.set_title('D&D Stock Price vs Performance Analysis\nBubble size = Market Cap, Color = Risk Level', 
                    fontsize=16, fontweight='bold', pad=20, color='#333333')
        
        # Linee di riferimento
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.6, linewidth=1)
        
        # Legenda per colori (rischio)
        legend_elements = [
            mpatches.Patch(color='#81C784', label='Low Risk (β < 0.8)'),
            mpatches.Patch(color='#FFCC80', label='Market Risk (β ≈ 1.0)'),
            mpatches.Patch(color='#F48FB1', label='High Risk (β > 1.2)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10, frameon=True)
        
        ax.grid(alpha=0.5, color='#D0D0D0')
        ax.set_facecolor('white')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "6_price_performance_bubble.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_7_volume_activity_analysis(self):
        """7. Analisi Volume e Attività di Trading"""
        print("📊 7. Generating Volume Activity Analysis...")
        
        if not self.stocks_data:
            print("No stock data available")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        fig.patch.set_facecolor('white')
        
        # Prepara dati volume
        volume_data = []
        for symbol, stock in self.stocks_data.items():
            volume_data.append({
                'name': stock['name'],
                'volume': stock['volume'],
                'daily_change_percent': stock['daily_change_percent'],
                'current_price': stock['current_price'],
                'market_cap': stock['market_cap']
            })
        
        df = pd.DataFrame(volume_data)
        df_sorted = df.sort_values('volume', ascending=False)
        
        # Plot 1: Volume ranking
        volume_millions = [vol / 1e6 for vol in df_sorted['volume']]
        colors1 = self.color_palettes['pastel_oranges'][:len(df_sorted)]
        
        bars1 = ax1.bar(range(len(df_sorted)), volume_millions, 
                       color=colors1, alpha=0.85, edgecolor='white', linewidth=2)
        
        ax1.set_xticks(range(len(df_sorted)))
        ax1.set_xticklabels(df_sorted['name'], rotation=45, ha='right', fontsize=10)
        ax1.set_ylabel('Trading Volume (Millions)', fontsize=12, fontweight='bold', color='#444444')
        ax1.set_title('Daily Trading Volume by Stock\nMarket Activity Ranking', 
                     fontsize=14, fontweight='bold', color='#333333')
        
        # Etichette valori
        for bar, vol_mil in zip(bars1, volume_millions):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + vol_mil*0.02,
                    f'{vol_mil:.1f}M', ha='center', fontweight='bold', fontsize=9, color='#444444')
        
        ax1.grid(axis='y', alpha=0.5, color='#D0D0D0')
        ax1.set_facecolor('white')
        
        # Plot 2: Volume vs Performance correlation
        volume_millions_all = [vol / 1e6 for vol in df['volume']]
        
        scatter = ax2.scatter(volume_millions_all, df['daily_change_percent'], 
                            s=150, alpha=0.8, c='#CE93D8',
                            edgecolors='white', linewidth=2)
        
        # Etichette
        for _, stock in df.iterrows():
            ax2.annotate(stock['name'][:8], (stock['volume']/1e6, stock['daily_change_percent']),
                        xytext=(8, 8), textcoords='offset points',
                        fontsize=9, fontweight='bold', color='#444444',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
        
        ax2.set_xlabel('Trading Volume (Millions)', fontsize=12, fontweight='bold', color='#444444')
        ax2.set_ylabel('Daily Change (%)', fontsize=12, fontweight='bold', color='#444444')
        ax2.set_title('Volume vs Performance Correlation\nTrading Activity Impact', 
                     fontsize=14, fontweight='bold', color='#333333')
        
        # Trend line
        z = np.polyfit(volume_millions_all, df['daily_change_percent'], 1)
        p = np.poly1d(z)
        ax2.plot(volume_millions_all, p(volume_millions_all), "r--", alpha=0.8, linewidth=2)
        
        # Correlation coefficient
        corr = np.corrcoef(volume_millions_all, df['daily_change_percent'])[0,1]
        ax2.text(0.05, 0.95, f'Correlation: {corr:.3f}', transform=ax2.transAxes,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9),
                fontsize=11, fontweight='bold', color='#444444')
        
        ax2.grid(alpha=0.5, color='#D0D0D0')
        ax2.set_facecolor('white')
        
        plt.suptitle('D&D Stock Trading Volume Analysis', fontsize=16, fontweight='bold', color='#333333')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "7_volume_activity_analysis.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def plot_8_comprehensive_financial_dashboard(self):
        """8. Dashboard Finanziario Comprensivo - FIXED"""
        print("📊 8. Generating Comprehensive Financial Dashboard...")
        
        if not self.stocks_data:
            print("No stock data available")
            return
        
        fig = plt.figure(figsize=(20, 14))
        fig.patch.set_facecolor('white')
        
        # Layout a griglia per dashboard
        gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1], width_ratios=[1, 1, 1])
        
        ax1 = fig.add_subplot(gs[0, :])   # Top full - Market summary
        ax2 = fig.add_subplot(gs[1, 0])   # Middle left - Top gainers
        ax3 = fig.add_subplot(gs[1, 1])   # Middle center - Top losers
        ax4 = fig.add_subplot(gs[1, 2])   # Middle right - Highest volume
        ax5 = fig.add_subplot(gs[2, :])   # Bottom full - Financial metrics heatmap
        
        # Prepara dati generali
        dashboard_data = []
        for symbol, stock in self.stocks_data.items():
            dashboard_data.append({
                'name': stock['name'],
                'symbol': symbol,
                'current_price': stock['current_price'],
                'daily_change': stock['daily_change'],
                'daily_change_percent': stock['daily_change_percent'],
                'volume': stock['volume'],
                'market_cap': stock['market_cap'],
                'pe_ratio': stock['pe_ratio'],
                'dividend_yield': stock['dividend_yield'],
                'beta': stock['beta']
            })
        
        df = pd.DataFrame(dashboard_data)
        
        # Plot 1: Market Summary Stats
        total_market_cap = df['market_cap'].sum()
        avg_change = df['daily_change_percent'].mean()
        gainers = len(df[df['daily_change_percent'] > 0])
        losers = len(df[df['daily_change_percent'] < 0])
        total_volume = df['volume'].sum()
        
        # Crea un grafico a barre per il summary
        metrics = ['Total Stocks', 'Market Cap ($B)', 'Avg Change (%)', 'Gainers', 'Losers', 'Volume (M)']
        values = [len(df), total_market_cap/1e9, avg_change, gainers, losers, total_volume/1e6]
        
        # Normalizza i valori per visualizzazione (0-100 scale)
        normalized_values = []
        for i, val in enumerate(values):
            if i == 0:  # Total stocks
                normalized_values.append(val * 5)  # Scale up
            elif i == 1:  # Market cap
                normalized_values.append(val * 10)  # Scale up
            elif i == 2:  # Avg change
                normalized_values.append(abs(val) * 10 + 50)  # Center around 50
            else:  # Gainers, losers, volume
                normalized_values.append(val)
        
        colors_summary = ['#81C784', '#64B5F6', '#FFB74D', '#A5D6A7', '#FFCDD2', '#CE93D8']
        bars = ax1.bar(metrics, normalized_values, color=colors_summary, alpha=0.8, edgecolor='white', linewidth=2)
        
        # Etichette con valori reali
        labels = [f'{len(df)}', f'${total_market_cap/1e9:.1f}B', f'{avg_change:+.1f}%', 
                 f'{gainers}', f'{losers}', f'{total_volume/1e6:.0f}M']
        
        for bar, label in zip(bars, labels):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    label, ha='center', fontweight='bold', fontsize=12, color='#444444')
        
        ax1.set_ylabel('Normalized Values', fontsize=12, fontweight='bold', color='#444444')
        ax1.set_title('D&D Market Summary Dashboard', fontsize=16, fontweight='bold', color='#333333')
        ax1.grid(axis='y', alpha=0.5, color='#D0D0D0')
        ax1.set_facecolor('white')
        
        # Plot 2: Top 5 Gainers
        top_gainers = df.nlargest(5, 'daily_change_percent')
        y_pos = range(len(top_gainers))
        
        bars2 = ax2.barh(y_pos, top_gainers['daily_change_percent'], 
                        color='#81C784', alpha=0.8, edgecolor='white', linewidth=2)
        
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels([name[:8] for name in top_gainers['name']], fontsize=9)
        ax2.set_xlabel('Change %', fontsize=10, fontweight='bold', color='#444444')
        ax2.set_title('Top 5 Gainers', fontsize=12, fontweight='bold', color='#333333')
        
        # Etichette valori
        for bar, change in zip(bars2, top_gainers['daily_change_percent']):
            ax2.text(change + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{change:+.1f}%', va='center', fontweight='bold', fontsize=9, color='#444444')
        
        ax2.grid(axis='x', alpha=0.5, color='#D0D0D0')
        ax2.set_facecolor('white')
        
        # Plot 3: Top 5 Losers
        top_losers = df.nsmallest(5, 'daily_change_percent')
        y_pos = range(len(top_losers))
        
        bars3 = ax3.barh(y_pos, top_losers['daily_change_percent'], 
                        color='#F48FB1', alpha=0.8, edgecolor='white', linewidth=2)
        
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels([name[:8] for name in top_losers['name']], fontsize=9)
        ax3.set_xlabel('Change %', fontsize=10, fontweight='bold', color='#444444')
        ax3.set_title('Top 5 Losers', fontsize=12, fontweight='bold', color='#333333')
        
        # Etichette valori
        for bar, change in zip(bars3, top_losers['daily_change_percent']):
            ax3.text(change - 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{change:+.1f}%', va='center', fontweight='bold', fontsize=9, color='#444444')
        
        ax3.grid(axis='x', alpha=0.5, color='#D0D0D0')
        ax3.set_facecolor('white')
        
        # Plot 4: Top 5 Volume
        top_volume = df.nlargest(5, 'volume')
        volume_millions = [vol/1e6 for vol in top_volume['volume']]
        y_pos = range(len(top_volume))
        
        bars4 = ax4.barh(y_pos, volume_millions, 
                        color='#FFCC80', alpha=0.8, edgecolor='white', linewidth=2)
        
        ax4.set_yticks(y_pos)
        ax4.set_yticklabels([name[:8] for name in top_volume['name']], fontsize=9)
        ax4.set_xlabel('Volume (M)', fontsize=10, fontweight='bold', color='#444444')
        ax4.set_title('Top 5 Volume', fontsize=12, fontweight='bold', color='#333333')
        
        # Etichette valori
        for bar, vol in zip(bars4, volume_millions):
            ax4.text(vol + 0.1, bar.get_y() + bar.get_height()/2, 
                    f'{vol:.1f}M', va='center', fontweight='bold', fontsize=9, color='#444444')
        
        ax4.grid(axis='x', alpha=0.5, color='#D0D0D0')
        ax4.set_facecolor('white')
        
        # Plot 5: Financial Metrics Heatmap
        metrics_data = df[['daily_change_percent', 'pe_ratio', 'dividend_yield', 'beta']].T
        metrics_data.columns = [name[:8] for name in df['name']]
        
        # Normalizza per comparison
        metrics_normalized = metrics_data.copy()
        for row in metrics_normalized.index:
            row_data = metrics_normalized.loc[row]
            if row_data.std() != 0:  # Evita divisione per zero
                metrics_normalized.loc[row] = (row_data - row_data.mean()) / row_data.std()
        
        im = ax5.imshow(metrics_normalized.values, cmap='RdYlGn', aspect='auto', 
                       interpolation='bilinear', alpha=0.8)
        
        ax5.set_xticks(range(len(metrics_normalized.columns)))
        ax5.set_xticklabels(metrics_normalized.columns, rotation=45, ha='right', fontsize=10)
        ax5.set_yticks(range(len(metrics_normalized.index)))
        ax5.set_yticklabels(['Daily Change %', 'P/E Ratio', 'Dividend %', 'Beta'], fontsize=11)
        ax5.set_title('Financial Metrics Heatmap (Normalized by Standard Deviations)', 
                     fontsize=14, fontweight='bold', color='#333333', pad=15)
        
        # Aggiungi valori numerici alle celle
        for i in range(len(metrics_normalized.index)):
            for j in range(len(metrics_normalized.columns)):
                value = metrics_normalized.iloc[i, j]
                ax5.text(j, i, f'{value:.1f}', ha='center', va='center',
                        fontweight='bold', fontsize=8, 
                        color='white' if abs(value) > 1 else 'black')
        
        # Colorbar per heatmap
        cbar = plt.colorbar(im, ax=ax5, fraction=0.046, pad=0.04)
        cbar.set_label('Standard Deviations from Mean', rotation=270, labelpad=15, fontsize=11)
        
        # plt.suptitle('D&D MARKET FINANCIAL DASHBOARD - Real-Time Analytics', fontsize=18, fontweight='bold', color='#333333', y=0.95)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "8_comprehensive_dashboard.png"), 
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

    def generate_all_market_charts(self):
        """Genera tutti gli 8 grafici di analisi finanziaria"""
        print("\n💰 GENERATING ALL 8 D&D MARKET ANALYSIS CHARTS")
        print("="*60)
        
        if not self.stocks_data:
            print("❌ No market data loaded. Please run market_simulator.py first.")
            return False
        
        charts = [
            ("P/E Ratio Valuation Analysis", self.plot_1_pe_ratio_valuation_analysis),
            ("Dividend Yield Ranking", self.plot_2_dividend_yield_ranking),
            ("Market Cap Visualization", self.plot_3_market_cap_visualization),
            ("Beta Risk Assessment", self.plot_4_beta_risk_assessment),
            ("Sector Performance Comparison", self.plot_5_sector_performance_comparison),
            ("Price vs Performance Bubble Chart", self.plot_6_price_vs_performance_bubble),
            ("Volume Activity Analysis", self.plot_7_volume_activity_analysis),
            ("Comprehensive Financial Dashboard", self.plot_8_comprehensive_financial_dashboard)
        ]
        
        successful = 0
        for i, (name, func) in enumerate(charts, 1):
            try:
                func()
                print(f"✅ {i:2d}. {name} completed")
                successful += 1
            except Exception as e:
                print(f"❌ {i:2d}. Error in {name}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n🎉 Market chart generation completed!")
        print(f"📁 Charts saved to: {self.output_dir}")
        print(f"✨ {successful}/8 charts generated successfully")
        print("💡 Features:")
        print("   • Enhanced pastel color palette with better visibility")
        print("   • Individual chart files for easy sharing")
        print("   • Professional financial analysis styling")
        print("   • Real data from market_simulator.py")
        print("   • CAPM, P/E, dividend yield, and beta analysis")
        print("   • Fixed dashboard with working visualizations")
        
        return successful == len(charts)

    def print_data_summary(self):
        """Stampa un riassunto dei dati caricati"""
        print(f"\n📊 DATA SUMMARY:")
        print(f"  Stocks loaded: {len(self.stocks_data)}")
        print(f"  Market report: {'✅' if self.market_report else '❌'}")
        print(f"  Market summary: {'✅' if self.market_summary else '❌'}")
        
        if self.stocks_data:
            df = pd.DataFrame([stock for stock in self.stocks_data.values()])
            print(f"  Price range: ${df['current_price'].min():.2f} - ${df['current_price'].max():.2f}")
            print(f"  Market cap range: ${df['market_cap'].min():,.0f} - ${df['market_cap'].max():,.0f}")
            print(f"  Beta range: {df['beta'].min():.2f} - {df['beta'].max():.2f}")
            print(f"  P/E range: {df['pe_ratio'].min():.1f} - {df['pe_ratio'].max():.1f}")

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    """Funzione principale per generare le visualizzazioni di mercato"""
    print("💰 D&D MARKET ANALYSIS VISUALIZER - ENHANCED COLORS")
    print("=" * 60)
    print("Analyzing financial data from market_simulator.py...")
    
    # Inizializza il visualizer
    visualizer = DNDMarketVisualizerFixed()
    
    # Stampa il data summary
    visualizer.print_data_summary()
    
    try:
        # Genera tutti gli 8 grafici finanziari
        success = visualizer.generate_all_market_charts()
        
        if success:
            print("\n🏆 All market charts generated successfully!")
            print("🎨 Each chart features enhanced pastel colors with better visibility")
            print("🔧 Dashboard fixed to show only working visualizations")
        else:
            print("\n⚠️ Some charts failed. Check error messages above.")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n🏁 Market chart generation complete!")
    return 0

if __name__ == "__main__":
    exit(main())