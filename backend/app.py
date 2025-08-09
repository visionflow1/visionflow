from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
from supabase import create_client, Client
from datetime import datetime, timezone
import io
import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io
import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

        return jsonify({'error': str(e)}), 500

# --- API: Download Individual Favorite ---
@app.route('/download-individual-favorite', methods=['POST', 'OPTIONS'])
def download_individual_favorite():
    if request.method == 'OPTIONS':
        return ('', 204)
    
    data = request.get_json()
    email = data.get('email')
    question = data.get('question')
    answer = data.get('answer')
    format_type = data.get('format', 'txt')  # txt, csv, pdf
    
    if not email or not question or not answer:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        if format_type == 'txt':
            content = f"VisionFlow AI - Single Favorite Export\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{'='*50}\n\nQ: {question}\n\nA: {answer}"
            
            response = app.response_class(
                content,
                mimetype='text/plain',
                headers={
                    'Content-Disposition': f'attachment; filename=visionflow_favorite.txt',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            return response
            
        elif format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Question', 'Answer', 'Date'])
            writer.writerow([question, answer, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            
            response = app.response_class(
                output.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=visionflow_favorite.csv',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            return response
            
        elif format_type == 'pdf':
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph("VisionFlow AI - Single Favorite Export", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Date
            date_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            date_para = Paragraph(date_text, styles['Normal'])
            story.append(date_para)
            story.append(Spacer(1, 0.3*inch))
            
            # Question
            q_text = f"<b>Q:</b> {question}"
            q_para = Paragraph(q_text, styles['Normal'])
            story.append(q_para)
            story.append(Spacer(1, 0.2*inch))
            
            # Answer
            a_text = f"<b>A:</b> {answer}"
            a_para = Paragraph(a_text, styles['Normal'])
            story.append(a_para)
            
            doc.build(story)
            buffer.seek(0)
            
            response = app.response_class(
                buffer.getvalue(),
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename=visionflow_favorite.pdf',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            return response
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- API: Bulk Download All Favorites ---
@app.route('/bulk-download-favorites', methods=['POST', 'OPTIONS'])
def bulk_download_favorites():
    if request.method == 'OPTIONS':
        return ('', 204)
    
    data = request.get_json()
    email = data.get('email')
    format_type = data.get('format', 'txt')  # txt, csv, pdf
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Get all favorites for the user
        result = supabase.table('favorites').select('*').eq('email', email).execute()
        if hasattr(result, 'error') and result.error:
            return jsonify({'error': str(result.error)}), 400
        
        favorites = result.data if hasattr(result, 'data') else []
        
        if not favorites:
            return jsonify({'error': 'No favorites found'}), 404
        
        if format_type == 'txt':
            content = f"VisionFlow AI - All Favorites Export\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nTotal Favorites: {len(favorites)}\n\n{'='*50}\n\n"
            
            for i, fav in enumerate(favorites, 1):
                content += f"=== FAVORITE {i} ===\nQ: {fav.get('question', '')}\nA: {fav.get('answer', '')}\n\n"
            
            response = app.response_class(
                content,
                mimetype='text/plain',
                headers={
                    'Content-Disposition': f'attachment; filename=visionflow_all_favorites.txt',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            return response
            
        elif format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Index', 'Question', 'Answer', 'Date'])
            
            for i, fav in enumerate(favorites, 1):
                writer.writerow([
                    i,
                    fav.get('question', ''),
                    fav.get('answer', ''),
                    fav.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                ])
            
            response = app.response_class(
                output.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=visionflow_all_favorites.csv',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            return response
            
        elif format_type == 'pdf':
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph("VisionFlow AI - All Favorites Export", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Header info
            date_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            date_para = Paragraph(date_text, styles['Normal'])
            story.append(date_para)
            
            total_text = f"Total Favorites: {len(favorites)}"
            total_para = Paragraph(total_text, styles['Normal'])
            story.append(total_para)
            story.append(Spacer(1, 0.3*inch))
            
            # Add each favorite
            for i, fav in enumerate(favorites, 1):
                # Favorite header
                fav_title = Paragraph(f"=== Favorite {i} ===", styles['Heading2'])
                story.append(fav_title)
                story.append(Spacer(1, 0.1*inch))
                
                # Question
                q_text = f"<b>Q:</b> {fav.get('question', '')}"
                q_para = Paragraph(q_text, styles['Normal'])
                story.append(q_para)
                story.append(Spacer(1, 0.1*inch))
                
                # Answer
                a_text = f"<b>A:</b> {fav.get('answer', '')}"
                a_para = Paragraph(a_text, styles['Normal'])
                story.append(a_para)
                story.append(Spacer(1, 0.3*inch))
            
            doc.build(story)
            buffer.seek(0)
            
            response = app.response_class(
                buffer.getvalue(),
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename=visionflow_all_favorites.pdf',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            return response
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- API: Download Individual Favorite ---
@app.route('/download-individual-favorite', methods=['POST', 'OPTIONS'])
def download_individual_favorite():
    if request.method == 'OPTIONS':
        return ('', 204)
    
    data = request.get_json()
    email = data.get('email')
    question = data.get('question')
    answer = data.get('answer')
    format_type = data.get('format', 'txt')  # txt, csv, pdf
    
    if not email or not question or not answer:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        if format_type == 'txt':
            content = f"VisionFlow AI - Single Favorite Export\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{'='*50}\n\nQ: {question}\n\nA: {answer}"
            
            response = app.response_class(
                content,
                mimetype='text/plain',
                headers={
                    'Content-Disposition': f'attachment; filename=visionflow_favorite.txt',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            return response
            
        elif format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Question', 'Answer', 'Date'])
            writer.writerow([question, answer, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            
            response = app.response_class(
                output.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=visionflow_favorite.csv',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            return response
            
        elif format_type == 'pdf':
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph("VisionFlow AI - Single Favorite Export", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Date
            date_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            date_para = Paragraph(date_text, styles['Normal'])
            story.append(date_para)
            story.append(Spacer(1, 0.3*inch))
            
            # Question
            q_text = f"<b>Q:</b> {question}"
            q_para = Paragraph(q_text, styles['Normal'])
            story.append(q_para)
            story.append(Spacer(1, 0.2*inch))
            
            # Answer
            a_text = f"<b>A:</b> {answer}"
            a_para = Paragraph(a_text, styles['Normal'])
            story.append(a_para)
            
            doc.build(story)
            buffer.seek(0)
            
            response = app.response_class(
                buffer.getvalue(),
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename=visionflow_favorite.pdf',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            return response
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- API: Bulk Download All Favorites ---
@app.route('/bulk-download-favorites', methods=['POST', 'OPTIONS'])
def bulk_download_favorites():
    if request.method == 'OPTIONS':
        return ('', 204)
    
    data = request.get_json()
    email = data.get('email')
    format_type = data.get('format', 'txt')  # txt, csv, pdf
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Get all favorites for the user
        result = supabase.table('favorites').select('*').eq('email', email).execute()
        if hasattr(result, 'error') and result.error:
            return jsonify({'error': str(result.error)}), 400
        
        favorites = result.data if hasattr(result, 'data') else []
        
        if not favorites:
            return jsonify({'error': 'No favorites found'}), 404
        
        if format_type == 'txt':
            content = f"VisionFlow AI - All Favorites Export\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nTotal Favorites: {len(favorites)}\n\n{'='*50}\n\n"
            
            for i, fav in enumerate(favorites, 1):
                content += f"=== FAVORITE {i} ===\nQ: {fav.get('question', '')}\nA: {fav.get('answer', '')}\n\n"
            
            response = app.response_class(
                content,
                mimetype='text/plain',
                headers={
                    'Content-Disposition': f'attachment; filename=visionflow_all_favorites.txt',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            return response
            
        elif format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Index', 'Question', 'Answer', 'Date'])
            
            for i, fav in enumerate(favorites, 1):
                writer.writerow([
                    i,
                    fav.get('question', ''),
                    fav.get('answer', ''),
                    fav.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                ])
            
            response = app.response_class(
                output.getvalue(),
                mimetype='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=visionflow_all_favorites.csv',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            return response
            
        elif format_type == 'pdf':
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph("VisionFlow AI - All Favorites Export", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Header info
            date_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            date_para = Paragraph(date_text, styles['Normal'])
            story.append(date_para)
            
            total_text = f"Total Favorites: {len(favorites)}"
            total_para = Paragraph(total_text, styles['Normal'])
            story.append(total_para)
            story.append(Spacer(1, 0.3*inch))
            
            # Add each favorite
            for i, fav in enumerate(favorites, 1):
                # Favorite header
                fav_title = Paragraph(f"=== Favorite {i} ===", styles['Heading2'])
                story.append(fav_title)
                story.append(Spacer(1, 0.1*inch))
                
                # Question
                q_text = f"<b>Q:</b> {fav.get('question', '')}"
                q_para = Paragraph(q_text, styles['Normal'])
                story.append(q_para)
                story.append(Spacer(1, 0.1*inch))
                
                # Answer
                a_text = f"<b>A:</b> {fav.get('answer', '')}"
                a_para = Paragraph(a_text, styles['Normal'])
                story.append(a_para)
                story.append(Spacer(1, 0.3*inch))
            
            doc.build(story)
            buffer.seek(0)
            
            response = app.response_class(
                buffer.getvalue(),
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename=visionflow_all_favorites.pdf',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            return response
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proxy-image')
def proxy_image():
