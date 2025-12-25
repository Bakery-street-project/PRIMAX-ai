# ==============================================================================
# PRIMSX CODEX - SCRIPT_3.PY
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================


# Generate Cat Article Content Pipeline with Super Prompt System
content_pipeline_code = '''#!/usr/bin/env python3
"""
Codex SuperLab Cat Article Content Pipeline
Automated content creation with AI-powered super prompts
"""

import os
import json
from datetime import datetime
import openai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
CONTENT_TRACKER_SHEET_ID = os.getenv("CONTENT_TRACKER_SHEET_ID")

openai.api_key = OPENAI_API_KEY

class ContentPipeline:
    def __init__(self):
        self.sheets_service = self._init_sheets()
        self.article_stages = [
            "Idea Generation",
            "Research & Planning",
            "Outline Creation",
            "Draft Writing",
            "Review & Edit",
            "SEO Optimization",
            "Publishing",
            "Promotion"
        ]
    
    def _init_sheets(self):
        """Initialize Google Sheets API"""
        creds = Credentials.from_authorized_user_file(SHEETS_CREDENTIALS)
        return build('sheets', 'v4', credentials=creds)
    
    def create_super_prompt(self, stage, topic, context={}):
        """
        Generate stage-specific super prompts for content creation
        Uses AI to create contextually aware, actionable prompts
        """
        
        prompt_templates = {
            "Idea Generation": f"""
                You are a creative content strategist for Codex SuperLab.
                
                Generate 5 unique, engaging article ideas about: {topic}
                
                Consider:
                - Current trends in the topic area
                - Audience pain points and interests
                - SEO potential and search intent
                - Unique angles that haven't been overused
                
                For each idea, provide:
                1. Article Title (attention-grabbing)
                2. One-sentence hook
                3. Key points to cover (3-5 bullet points)
                4. Target audience persona
                5. Estimated word count and complexity level
                
                Format as JSON array.
            """,
            
            "Research & Planning": f"""
                You are a research assistant for a {topic} article.
                
                Current article context: {json.dumps(context, indent=2)}
                
                Create a comprehensive research plan:
                
                1. **Key Questions to Answer:**
                   - List 10 specific questions this article must address
                
                2. **Recommended Sources:**
                   - Suggest 5-7 authoritative sources to consult
                   - Include academic papers, industry blogs, expert interviews
                
                3. **Data Points to Gather:**
                   - Statistics, case studies, examples needed
                
                4. **Expert Perspectives:**
                   - Which experts or thought leaders should be referenced?
                
                5. **Competitor Analysis:**
                   - What gaps exist in current content on this topic?
                
                Output as structured markdown.
            """,
            
            "Outline Creation": f"""
                You are a professional content outliner for: {topic}
                
                Article context: {json.dumps(context, indent=2)}
                
                Create a detailed article outline with:
                
                **Article Structure:**
                - Hook/Introduction (2-3 sentences)
                - Main sections (H2 headers) with:
                  - Subsections (H3 headers)
                  - Key points to cover
                  - Examples/data to include
                  - Estimated word count per section
                - Conclusion with clear takeaways
                
                **SEO Elements:**
                - Primary keyword placement strategy
                - Internal linking opportunities (3-5)
                - Meta description (150-160 chars)
                
                **Engagement Hooks:**
                - Where to place images/charts
                - Call-to-action placements
                - Interactive elements (if any)
                
                Make it actionable and comprehensive.
            """,
            
            "Draft Writing": f"""
                You are an expert content writer specializing in {topic}.
                
                Using this outline: {json.dumps(context.get('outline', {}), indent=2)}
                
                Write a compelling, well-researched article draft.
                
                Writing Guidelines:
                - Conversational yet authoritative tone
                - Use active voice, short paragraphs
                - Include transitional phrases
                - Incorporate storytelling where relevant
                - Add specific examples and data points
                - Natural keyword integration (avoid stuffing)
                
                Section to write: {context.get('current_section', 'Introduction')}
                
                Target word count: {context.get('word_count', 800)}
                
                Write engaging, value-packed content that keeps readers hooked.
            """,
            
            "Review & Edit": f"""
                You are a professional editor reviewing a draft article on {topic}.
                
                Current draft: {context.get('draft', '')[:1000]}... [truncated]
                
                Provide comprehensive editing feedback:
                
                **Content Quality:**
                - Clarity and flow issues
                - Gaps in logic or missing information
                - Redundant or off-topic sections
                
                **Style & Tone:**
                - Inconsistencies in voice
                - Overly complex sentences
                - Passive voice instances
                
                **Technical:**
                - Grammar and punctuation errors
                - Formatting improvements
                - Citation/source additions needed
                
                **Engagement:**
                - Where the article loses momentum
                - Opportunities for stronger hooks
                - Call-to-action effectiveness
                
                Provide specific line-by-line suggestions with examples.
            """,
            
            "SEO Optimization": f"""
                You are an SEO specialist optimizing content about {topic}.
                
                Article data: {json.dumps(context, indent=2)}
                
                Provide SEO optimization checklist:
                
                **Keyword Strategy:**
                - Primary keyword density check (aim 1-2%)
                - LSI keywords to add (10 suggestions)
                - Long-tail keyword opportunities
                
                **On-Page SEO:**
                - Title tag optimization (50-60 chars)
                - Meta description (150-160 chars)
                - Header hierarchy review (H1-H6)
                - Image alt text suggestions
                - Internal linking strategy (5-7 links)
                
                **Content Structure:**
                - Readability score target
                - Paragraph length optimization
                - Bullet point and list opportunities
                
                **Featured Snippet Potential:**
                - Sections that could rank for featured snippets
                - How to format them
                
                Make specific, actionable recommendations.
            """,
            
            "Publishing": f"""
                You are a publishing coordinator for {topic} content.
                
                Article ready for: {context.get('platform', 'blog')}
                
                Create publishing checklist:
                
                **Pre-Publish:**
                - [ ] Final proofread completed
                - [ ] All images optimized and uploaded
                - [ ] Meta tags configured
                - [ ] Internal links added
                - [ ] External links validated
                - [ ] Social media images created
                - [ ] Author bio and CTA finalized
                
                **Platform-Specific:**
                - CMS configuration steps
                - Category and tag selection
                - Featured image requirements
                - Permalink structure
                
                **Quality Checks:**
                - Mobile responsiveness
                - Page load speed
                - Broken link check
                - Schema markup validation
                
                **Scheduling:**
                - Optimal publish time suggestion
                - Timezone considerations
                
                Provide step-by-step publishing protocol.
            """,
            
            "Promotion": f"""
                You are a content promotion strategist for: {topic}
                
                Article URL: {context.get('url', 'TBD')}
                Published: {context.get('publish_date', datetime.now().strftime('%Y-%m-%d')}}
                
                Create comprehensive promotion plan:
                
                **Social Media Strategy:**
                - Platform-specific posts (Twitter, LinkedIn, Facebook)
                - Post variations (5-7 per platform)
                - Optimal posting times
                - Hashtag strategy (#15-20 relevant tags)
                - Visual content requirements
                
                **Email Marketing:**
                - Newsletter inclusion strategy
                - Email subject line options (5 variations)
                - Snippet/teaser text
                - Segmentation recommendations
                
                **Community Engagement:**
                - Reddit communities to share in
                - Discord/Slack channels
                - Forum discussions to join
                - Comment engagement strategy
                
                **Outreach:**
                - Influencers to notify (5-10)
                - Guest post opportunities
                - Backlink building targets
                
                **Paid Promotion:**
                - Budget allocation suggestions
                - Ad copy variations
                - Targeting parameters
                
                **Timeline:**
                - Week 1: Immediate actions
                - Week 2-4: Sustained engagement
                - Month 2-3: Repurposing strategy
                
                Make it actionable with templates and examples.
            """
        }
        
        # Get base template
        base_prompt = prompt_templates.get(stage, "Generate content guidance for this stage.")
        
        # Use OpenAI to generate contextual super prompt
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert content creation assistant."},
                    {"role": "user", "content": base_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            super_prompt = response['choices'][0]['message']['content']
            return super_prompt
            
        except Exception as e:
            print(f"Error generating super prompt: {e}")
            return base_prompt
    
    def create_article_project(self, topic, target_date=None):
        """
        Initialize new article project with full pipeline
        """
        project_id = f"ART_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        project = {
            "id": project_id,
            "topic": topic,
            "created": datetime.now().isoformat(),
            "target_date": target_date or (datetime.now() + timedelta(days=7)).isoformat(),
            "current_stage": "Idea Generation",
            "stages": {},
            "metadata": {}
        }
        
        # Generate super prompt for first stage
        first_prompt = self.create_super_prompt("Idea Generation", topic, {})
        project["stages"]["Idea Generation"] = {
            "status": "Active",
            "super_prompt": first_prompt,
            "started": datetime.now().isoformat(),
            "output": None
        }
        
        # Log to Google Sheets
        self._log_to_sheets(project)
        
        print(f"✅ Article project created: {project_id}")
        print(f"📝 Topic: {topic}")
        print(f"🎯 Target completion: {target_date}")
        print(f"\\n{'='*60}")
        print("SUPER PROMPT FOR IDEA GENERATION:")
        print(f"{'='*60}")
        print(first_prompt)
        
        return project
    
    def advance_stage(self, project_id, output_data):
        """
        Complete current stage and advance to next with new super prompt
        """
        # Load project (from file or database)
        project = self._load_project(project_id)
        
        current_stage = project["current_stage"]
        current_idx = self.article_stages.index(current_stage)
        
        # Mark current stage complete
        project["stages"][current_stage]["status"] = "Complete"
        project["stages"][current_stage]["completed"] = datetime.now().isoformat()
        project["stages"][current_stage]["output"] = output_data
        
        # Move to next stage if not at end
        if current_idx < len(self.article_stages) - 1:
            next_stage = self.article_stages[current_idx + 1]
            project["current_stage"] = next_stage
            
            # Generate super prompt for next stage
            context = {
                "previous_output": output_data,
                "all_outputs": {s: project["stages"][s].get("output") 
                               for s in project["stages"] if project["stages"][s].get("output")}
            }
            
            next_prompt = self.create_super_prompt(next_stage, project["topic"], context)
            
            project["stages"][next_stage] = {
                "status": "Active",
                "super_prompt": next_prompt,
                "started": datetime.now().isoformat(),
                "output": None
            }
            
            print(f"\\n{'='*60}")
            print(f"✅ {current_stage} completed!")
            print(f"➡️  Moving to: {next_stage}")
            print(f"{'='*60}")
            print("NEW SUPER PROMPT:")
            print(f"{'='*60}")
            print(next_prompt)
        else:
            print(f"\\n🎉 Article pipeline complete! All stages finished.")
            project["status"] = "Complete"
        
        # Save project
        self._save_project(project)
        self._update_sheets(project)
        
        return project
    
    def _log_to_sheets(self, project):
        """Log new project to tracking sheet"""
        range_name = "ContentPipeline!A:G"
        values = [[
            project["id"],
            project["topic"],
            project["current_stage"],
            project["created"],
            project["target_date"],
            "Active",
            json.dumps(project["metadata"])
        ]]
        
        body = {'values': values}
        self.sheets_service.spreadsheets().values().append(
            spreadsheetId=CONTENT_TRACKER_SHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
    
    def _update_sheets(self, project):
        """Update project status in sheet"""
        # Find and update row
        pass
    
    def _load_project(self, project_id):
        """Load project from storage"""
        try:
            with open(f"projects/{project_id}.json", "r") as f:
                return json.load(f)
        except:
            return None
    
    def _save_project(self, project):
        """Save project to storage"""
        os.makedirs("projects", exist_ok=True)
        with open(f"projects/{project['id']}.json", "w") as f:
            json.dump(project, f, indent=2)

def main():
    """Example usage"""
    pipeline = ContentPipeline()
    
    # Create new cat article project
    project = pipeline.create_article_project(
        topic="The Ultimate Guide to Cat Behavior: Understanding Your Feline Friend",
        target_date="2025-11-01"
    )
    
    # Simulate completing idea generation stage
    # In real use, human or AI would provide this output
    idea_output = {
        "selected_idea": "Deep dive into cat body language and communication",
        "target_audience": "New cat owners and cat enthusiasts",
        "key_points": [
            "Tail positions and meanings",
            "Ear movements and emotions",
            "Vocal communication patterns",
            "Scent marking behavior",
            "Play vs aggressive behavior"
        ]
    }
    
    # Advance to next stage
    # project = pipeline.advance_stage(project["id"], idea_output)

if __name__ == "__main__":
    main()
'''

# Save content pipeline implementation
with open("cat_article_content_pipeline.py", "w") as f:
    f.write(content_pipeline_code)

print("Cat Article Content Pipeline created: cat_article_content_pipeline.py")
