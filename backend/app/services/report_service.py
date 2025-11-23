"""
Report Agent Service - Generates PDF reports from analysis results
"""
from typing import Optional
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models.schemas import (
    AnalysisResponse,
    YieldPrediction,
    OptimizationResult,
    Recommendation,
    ProcessParameters
)


class ReportAgent:
    """Agent responsible for generating PDF reports"""
    
    def __init__(self):
        self.name = "Report Agent"
    
    def generate_pdf_report(self, analysis_response: AnalysisResponse, wafer_id: str = "WAFER_001") -> BytesIO:
        """Generate a comprehensive PDF report from analysis results"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=10
        )
        
        # Title
        elements.append(Paragraph("🔬 Semiconductor Yield Analysis Report", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        metadata_data = [
            ['Wafer ID:', wafer_id],
            ['Report Date:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Analysis Type:', 'Multi-Agent Yield Prediction & Optimization']
        ]
        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f7fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2d3748')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(metadata_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        elements.append(Paragraph("📊 Executive Summary", heading_style))
        
        prediction = analysis_response.prediction
        optimization = analysis_response.optimization
        
        summary_data = [
            ['Metric', 'Value'],
            ['Predicted Yield', f"{prediction.predicted_yield:.2f}%"],
            ['Confidence Level', f"{prediction.confidence * 100:.1f}%"],
            ['Current Yield', f"{optimization.current_yield:.2f}%"],
            ['Optimized Yield', f"{optimization.optimized_yield:.2f}%"],
            ['Potential Improvement', f"+{optimization.improvement_percentage:.2f}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')])
        ]))
        elements.append(summary_table)
        elements.append(PageBreak())
        
        # Yield Prediction Details
        elements.append(Paragraph("📈 Yield Prediction Analysis", heading_style))
        
        pred_text = f"""
        The prediction model has analyzed the wafer data and process parameters to forecast a yield of 
        <b>{prediction.predicted_yield:.2f}%</b> with a confidence level of <b>{prediction.confidence * 100:.1f}%</b>.
        """
        elements.append(Paragraph(pred_text, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        if prediction.factors:
            elements.append(Paragraph("Key Factors Affecting Yield:", subheading_style))
            for i, factor in enumerate(prediction.factors, 1):
                elements.append(Paragraph(f"{i}. {factor}", styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Parameter Optimization
        elements.append(Paragraph("⚙️ Parameter Optimization", heading_style))
        
        current_params = analysis_response.current_parameters
        opt_params = optimization.recommended_parameters
        
        param_data = [
            ['Parameter', 'Current Value', 'Optimized Value', 'Change', 'Unit'],
            [
                'Temperature',
                f"{current_params.temperature:.2f}",
                f"{opt_params.temperature:.2f}",
                f"{opt_params.temperature - current_params.temperature:+.2f}",
                '°C'
            ],
            [
                'Etch Time',
                f"{current_params.etch_time:.2f}",
                f"{opt_params.etch_time:.2f}",
                f"{opt_params.etch_time - current_params.etch_time:+.2f}",
                's'
            ],
            [
                'Exposure Dose',
                f"{current_params.exposure_dose:.2f}",
                f"{opt_params.exposure_dose:.2f}",
                f"{opt_params.exposure_dose - current_params.exposure_dose:+.2f}",
                'mJ/cm²'
            ]
        ]
        
        param_table = Table(param_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1*inch, 0.8*inch])
        param_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc'), colors.white])
        ]))
        elements.append(param_table)
        elements.append(PageBreak())
        
        # Recommendations
        elements.append(Paragraph("💡 Actionable Recommendations", heading_style))
        
        recommendations = analysis_response.recommendations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                action_icon = "🔽" if rec.action == "reduce" else "🔼" if rec.action == "increase" else "⚙️"
                elements.append(Paragraph(
                    f"{action_icon} <b>Recommendation {i}: {rec.action.capitalize()} {rec.parameter.replace('_', ' ')}</b>",
                    subheading_style
                ))
                elements.append(Paragraph(rec.description, styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))
                
                rec_data = [
                    ['Metric', 'Value'],
                    ['Current Value', f"{rec.current_value:.2f}"],
                    ['Recommended Value', f"{rec.recommended_value:.2f}"],
                    ['Expected Improvement', f"+{rec.improvement:.2f}%"]
                ]
                
                rec_table = Table(rec_data, colWidths=[2.5*inch, 2.5*inch])
                rec_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c6f6d5')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#22543d')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                ]))
                elements.append(rec_table)
                elements.append(Spacer(1, 0.2*inch))
        else:
            elements.append(Paragraph(
                "No specific recommendations at this time. Current parameters are near optimal.",
                styles['Normal']
            ))
        
        elements.append(PageBreak())
        
        # Agent Status
        elements.append(Paragraph("🤖 Multi-Agent System Status", heading_style))
        
        agent_data = [
            ['Agent', 'Status', 'Description'],
            ['Data Agent', '✅ Complete', 'Processed wafer data and metrology information'],
            ['Prediction Agent', '✅ Complete', f'Yield predicted: {prediction.predicted_yield:.2f}%'],
            ['Optimization Agent', '✅ Complete', f'Parameters optimized with {optimization.improvement_percentage:.2f}% improvement'],
            ['Recommendation Agent', '✅ Complete', f'Generated {len(recommendations)} actionable recommendations'],
            ['Report Agent', '✅ Complete', 'PDF report generated successfully']
        ]
        
        agent_table = Table(agent_data, colWidths=[2*inch, 1.5*inch, 3.5*inch])
        agent_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')] * 3)
        ]))
        elements.append(agent_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_text = f"""
        <i>This report was generated by the Semiconductor Yield Prediction & Optimization Multi-Agent System.</i><br/>
        <i>For questions or support, please contact your system administrator.</i>
        """
        elements.append(Paragraph(footer_text, styles['Italic']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

