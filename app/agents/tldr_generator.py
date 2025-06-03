from app.agents.base_agent import BaseAgent
from app.models.schemas import PaperAnalysis, TLDRContent
from app.services.image_service import image_service


class TLDRGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__("TLDRGenerator", model_type="light")

    async def process(self, analysis: PaperAnalysis) -> TLDRContent:
        """Generate platform-specific social media content"""
        # LinkedIn Post
        linkedin_prompt = f"""
        Create a professional LinkedIn post about this research:
        
        Title: {analysis.title}
        Key Findings: {", ".join(analysis.key_findings)}
        Methodology: {analysis.methodology}
        
        Requirements:
        - Professional tone
        - 1200 characters max
        - Include relevant hashtags
        - Encourage engagement
        - Highlight practical implications
        Make sure to include the key findings and methodology in bullet fashion.
        Don't include any other information except the post content. No additional headers or ending text in the response.
        """

        # Twitter Thread
        twitter_prompt = f"""
        Create a Twitter thread (3-5 tweets) about this research:
        
        Title: {analysis.title}
        Key Findings: {", ".join(analysis.key_findings)}
        Methodology: {analysis.methodology}

        Requirements:
        - Each tweet max 280 characters
        - Start with hook
        - Include thread numbers (1/n)
        - End with call to action

        Make sure to include the key findings and methodology.
        Don't include any other information except the thread content. No additional headers or ending text in the response.
        """

        # Facebook Post
        facebook_prompt = f"""
        Create an engaging Facebook post about this research:
        
        Title: {analysis.title}
        Key Finding: {analysis.key_findings if analysis.key_findings else analysis.conclusion}
        Methodology: {analysis.methodology}

        Requirements:
        - Conversational tone
        - Ask questions to encourage comments
        - Include emojis appropriately
        - 500 characters max

        Make sure to include the key findings and methodology.
        Don't include any other information except the post content. No additional headers or ending text in the response.
        """

        # Instagram Caption
        instagram_prompt = f"""
        Create an Instagram caption about this research:
        
        Title: {analysis.title}
        Key Finding: {analysis.key_findings if analysis.key_findings else analysis.conclusion}
        Methodology: {analysis.methodology}

        Requirements:
        - Visual-friendly language
        - Include relevant emojis
        - Use line breaks for readability
        - Include hashtags
        - 2200 characters max

        Make sure to include the key findings and methodology.
        Don't include any other information except the caption content. No additional headers or ending text in the response.
        """

        # Generate all content
        linkedin_post = await self._generate_platform_content(linkedin_prompt)
        twitter_thread = await self._generate_twitter_thread(twitter_prompt)
        facebook_post = await self._generate_platform_content(facebook_prompt)
        instagram_caption = await self._generate_platform_content(instagram_prompt)
        hashtags = self._generate_hashtags(analysis)

        # Generate images for all platforms
        try:
            images = await image_service.generate_all_social_images(analysis)
        except Exception as e:
            print(f"Error generating images: {e!s}")
            images = {
                "linkedin": None,
                "twitter": None,
                "facebook": None,
                "instagram": None,
            }

        return TLDRContent(
            linkedin_post=linkedin_post,
            twitter_thread=twitter_thread,
            facebook_post=facebook_post,
            instagram_caption=instagram_caption,
            hashtags=hashtags,
            linkedin_image=images.get("linkedin"),
            twitter_image=images.get("twitter"),
            facebook_image=images.get("facebook"),
            instagram_image=images.get("instagram"),
        )

    async def _generate_platform_content(self, prompt: str) -> str:
        """Generate content for a specific platform"""
        messages = [
            {
                "role": "system",
                "content": "You are a social media expert who creates engaging, platform-specific content.",
            },
            {"role": "user", "content": prompt},
        ]
        return await self.generate_response(messages, temperature=0.8)

    async def _generate_twitter_thread(self, prompt: str) -> list:
        """Generate Twitter thread as list of tweets"""
        response = await self._generate_platform_content(prompt)

        # Split into individual tweets
        tweets = []
        lines = response.split("\n")
        current_tweet = ""

        for line in lines:
            line = line.strip()
            if line and (
                line.startswith(("1/", "2/", "3/", "4/", "5/"))
                or line.startswith(("1.", "2.", "3.", "4.", "5."))
            ):
                if current_tweet:
                    tweets.append(current_tweet.strip())
                current_tweet = line
            elif line:
                current_tweet += " " + line

        if current_tweet:
            tweets.append(current_tweet.strip())

        return tweets[:5]  # Limit to 5 tweets

    def _generate_hashtags(self, analysis: PaperAnalysis) -> list:
        """Generate relevant hashtags"""
        hashtags = ["#research", "#science", "#academic"]

        # Add field-specific hashtags
        title_lower = analysis.title.lower()
        if "ai" in title_lower or "artificial intelligence" in title_lower:
            hashtags.extend(["#AI", "#MachineLearning", "#Technology"])
        elif "machine learning" in title_lower:
            hashtags.extend(["#MachineLearning", "#DataScience", "#AI"])
        elif "computer" in title_lower:
            hashtags.extend(["#ComputerScience", "#Technology", "#Programming"])
        elif "biology" in title_lower or "medical" in title_lower:
            hashtags.extend(["#Biology", "#Medicine", "#Healthcare"])
        elif "physics" in title_lower:
            hashtags.extend(["#Physics", "#Science"])
        elif "chemistry" in title_lower:
            hashtags.extend(["#Chemistry", "#Science"])

        return hashtags[:10]
