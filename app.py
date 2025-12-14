import logging
import smtplib
import json
import os

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from agents.news_agent import news_agent

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/news")
async def send_news():
    try:
        # Invoke the agent
        response = news_agent.invoke({"messages": "Today's News!!!"})
        
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
        logger.info(f"Messages type: {type(response.get('messages', []))}")
        logger.info(f"Messages length: {len(response.get('messages', [])) if isinstance(response.get('messages'), list) else 'N/A'}")
        
        # Get the last message content
        last_message = response["messages"][-1]
        
        logger.info(f"Last message type: {type(last_message)}")
        logger.info(f"Last message: {last_message}")
        
        if hasattr(last_message, 'content') and isinstance(last_message.content, list):
            content = last_message.content[0]['text']
        elif hasattr(last_message, 'content'):
            content = last_message.content
        else:
            content = str(last_message)
        
        logger.info(f"Content type: {type(content)}")
        logger.info(f"Content preview: {content[:200] if isinstance(content, str) else content}")
        
        if content.startswith('```json'):
            content = content.split('```json')[1].split('```')[0].strip()
        elif content.startswith('```'):
            content = content.split('```')[1].split('```')[0].strip()
        
        news_data = json.loads(content)
        
        logger.info(f"News Data preview: {str(news_data)[:100]}")
        
        # Create HTML email
        html_content = create_html_email(news_data)
        
        # Send email
        send_email("balaharinath.dev@gmail.com", html_content)
        
        return {"status": "success", "message": "News sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_html_email(news_data):
    html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 36px;
                    font-weight: 700;
                    letter-spacing: -0.5px;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 16px;
                }}
                .content {{
                    padding: 40px;
                }}
                .section {{
                    margin-bottom: 50px;
                }}
                .section-title {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #667eea;
                    margin-bottom: 25px;
                    padding-bottom: 10px;
                    border-bottom: 3px solid #667eea;
                }}
                .news-item {{
                    background: #f8f9fa;
                    border-radius: 12px;
                    padding: 25px;
                    margin-bottom: 20px;
                    border-left: 4px solid #667eea;
                    transition: transform 0.2s;
                }}
                .news-title {{
                    font-size: 20px;
                    font-weight: 600;
                    color: #1a1a1a;
                    margin-bottom: 12px;
                    line-height: 1.4;
                }}
                .news-link {{
                    color: #667eea;
                    text-decoration: none;
                    font-weight: 500;
                }}
                .news-link:hover {{
                    text-decoration: underline;
                }}
                .news-meta {{
                    font-size: 13px;
                    color: #666;
                    margin-bottom: 15px;
                }}
                .news-content {{
                    color: #4a5568;
                    line-height: 1.7;
                    font-size: 15px;
                }}
                .field {{
                    margin-bottom: 15px;
                }}
                .field-label {{
                    font-weight: 600;
                    color: #667eea;
                    margin-bottom: 5px;
                    font-size: 14px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .field-content {{
                    color: #4a5568;
                    line-height: 1.7;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 30px;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📰 Daily News Digest</h1>
                    <p>{news_data.get('generated_at', 'Today')}</p>
                </div>
                
                <div class="content">
                    <!-- Global Enterprise Tech -->
                    <div class="section">
                        <h2 class="section-title">🚀 Global Enterprise Tech</h2>
                        {"".join([f'''
                        <div class="news-item">
                            <div class="news-title"><a href="{item['link']}" class="news-link">{item['title']}</a></div>
                            <div class="news-meta">{item.get('published', '')}</div>
                            <div class="field">
                                <div class="field-label">Summary</div>
                                <div class="field-content">{item.get('summary', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Context</div>
                                <div class="field-content">{item.get('context', '')}</div>
                            </div>
                            {f'<div class="field"><div class="field-label">Related Developments</div><div class="field-content">{item.get("related_developments", "")}</div></div>' if item.get('related_developments') else ''}
                        </div>
                        ''' for item in news_data.get('global_enterprise_tech', [])])}
                    </div>
                    
                    <!-- World Politics -->
                    <div class="section">
                        <h2 class="section-title">🌍 World Politics</h2>
                        {"".join([f'''
                        <div class="news-item">
                            <div class="news-title"><a href="{item['link']}" class="news-link">{item['title']}</a></div>
                            <div class="news-meta">{item.get('published', '')}</div>
                            <div class="field">
                                <div class="field-label">Summary</div>
                                <div class="field-content">{item.get('summary', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Background</div>
                                <div class="field-content">{item.get('background', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Key Players</div>
                                <div class="field-content">{item.get('key_players', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Impact Analysis</div>
                                <div class="field-content">{item.get('impact_analysis', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Complete Picture</div>
                                <div class="field-content">{item.get('complete_picture', '')}</div>
                            </div>
                        </div>
                        ''' for item in news_data.get('world_politics', [])])}
                    </div>
                    
                    <!-- Indian Politics -->
                    <div class="section">
                        <h2 class="section-title">🇮🇳 Indian Politics</h2>
                        {"".join([f'''
                        <div class="news-item">
                            <div class="news-title"><a href="{item['link']}" class="news-link">{item['title']}</a></div>
                            <div class="news-meta">{item.get('published', '')}</div>
                            <div class="field">
                                <div class="field-label">Summary</div>
                                <div class="field-content">{item.get('summary', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Background</div>
                                <div class="field-content">{item.get('background', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Key Players</div>
                                <div class="field-content">{item.get('key_players', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Impact Analysis</div>
                                <div class="field-content">{item.get('impact_analysis', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Complete Picture</div>
                                <div class="field-content">{item.get('complete_picture', '')}</div>
                            </div>
                        </div>
                        ''' for item in news_data.get('indian_politics', [])])}
                    </div>
                    
                    <!-- Business & Market -->
                    <div class="section">
                        <h2 class="section-title">💼 Business & Market</h2>
                        {"".join([f'''
                        <div class="news-item">
                            <div class="news-title"><a href="{item['link']}" class="news-link">{item['title']}</a></div>
                            <div class="news-meta">{item.get('published', '')}</div>
                            <div class="field">
                                <div class="field-label">Summary</div>
                                <div class="field-content">{item.get('summary', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">What It Is</div>
                                <div class="field-content">{item.get('what_it_is', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Why It Matters</div>
                                <div class="field-content">{item.get('why_it_matters', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Impact Analysis</div>
                                <div class="field-content">{item.get('impact_analysis', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Market Context</div>
                                <div class="field-content">{item.get('market_context', '')}</div>
                            </div>
                            <div class="field">
                                <div class="field-label">Investor Perspective</div>
                                <div class="field-content">{item.get('investor_perspective', '')}</div>
                            </div>
                        </div>
                        ''' for item in news_data.get('business_market', [])])}
                    </div>
                </div>
                
                <div class="footer">
                    <p>📧 Daily News Digest • Curated with AI</p>
                    <p>Stay informed, stay ahead.</p>
                </div>
            </div>
        </body>
        </html>
    """
    return html

def send_email(recipient_email, html_content):
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📰 Your Daily News Digest"
    msg["From"] = sender_email
    msg["To"] = recipient_email
    
    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)