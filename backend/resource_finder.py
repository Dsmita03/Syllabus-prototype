# resource_finder.py

import requests
from bs4 import BeautifulSoup
import urllib.parse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

# ---------------- Web Search (Multiple Methods) ----------------
def search_web(query, max_results=6):
    """Search web using multiple methods with fallbacks"""
    print(f"Searching web for: {query}")
    results = []
    
    # Method 1: Try new ddgs package
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            search_results = ddgs.text(query, max_results=max_results)
            for r in search_results:
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                    "source": "web"
                })
            if results:
                logger.info(f"Found {len(results)} results using ddgs")
                return results
    except Exception as e:
        logger.warning(f"ddgs search failed: {e}")
    
    # Method 2: Try old duckduckgo_search package
    # try:
    #     from duckduckgo_search import DDGS as DDGS_OLD
    #     with DDGS_OLD() as ddgs:
    #         search_results = ddgs.text(query, max_results=max_results)
    #         for r in search_results:
    #             results.append({
    #                 "title": r.get("title", ""),
    #                 "url": r.get("href", ""),
    #                 "snippet": r.get("body", ""),
    #                 "source": "web"
    #             })
    #         if results:
    #             logger.info(f"Found {len(results)} results using duckduckgo_search")
    #             return results
    # except Exception as e:
    #     logger.warning(f"duckduckgo_search failed: {e}")
    
    # Method 3: Fallback to manual scraping (Google Scholar, educational sites)
    results = search_web_fallback(query, max_results)
    
    return results


def search_web_fallback(query, max_results=6):
    """Fallback web search using direct HTTP requests"""
    results = []
    
    try:
        # Search Google Scholar (better for academic content)
        scholar_query = urllib.parse.quote_plus(query)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        url = f"https://scholar.google.com/scholar?q={scholar_query}&hl=en"
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse Google Scholar results
            for item in soup.select('.gs_ri')[:max_results]:
                title_elem = item.select_one('.gs_rt')
                snippet_elem = item.select_one('.gs_rs')
                link_elem = item.select_one('.gs_rt a')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    # Remove citation markers like [PDF], [HTML]
                    title = title.replace('[PDF]', '').replace('[HTML]', '').strip()
                    
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    url = link_elem['href'] if link_elem and link_elem.has_attr('href') else ""
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "source": "web"
                        })
            
            logger.info(f"Found {len(results)} results using fallback search")
    
    except Exception as e:
        logger.error(f"Fallback search failed: {e}")
    
    return results


# ---------------- YouTube Search (Fixed) ----------------
def search_youtube(query, max_results=4):
    """Search YouTube with error handling"""
    videos = []
    
    try:
        from youtubesearchpython import VideosSearch
        
        search = VideosSearch(query, limit=max_results)
        data = search.result()
        
        if data and "result" in data:
            for v in data["result"]:
                snippet = ""
                if v.get("descriptionSnippet"):
                    snippet = " ".join([
                        d.get("text", "") 
                        for d in v["descriptionSnippet"]
                    ])
                
                videos.append({
                    "title": v.get("title", ""),
                    "url": v.get("link", ""),
                    "snippet": snippet,
                    "source": "youtube"
                })
        
        logger.info(f"Found {len(videos)} YouTube videos")
        
    except Exception as e:
        logger.error(f"YouTube search failed: {e}")
        # Fallback: construct manual YouTube search URL
        videos = search_youtube_fallback(query, max_results)
    
    return videos


def search_youtube_fallback(query, max_results=4):
    """Fallback YouTube search using direct URL construction"""
    videos = []
    
    try:
        search_query = urllib.parse.quote_plus(query)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        url = f"https://www.youtube.com/results?search_query={search_query}"
        
        # Just provide the search URL as a resource
        videos.append({
            "title": f"YouTube Search: {query[:50]}",
            "url": f"https://www.youtube.com/results?search_query={search_query}",
            "snippet": "Click to search YouTube for educational videos on this topic",
            "source": "youtube"
        })
        
        logger.info("Using YouTube search URL fallback")
        
    except Exception as e:
        logger.error(f"YouTube fallback failed: {e}")
    
    return videos


# ---------------- Ranking ----------------
def rank_resources(query, resources):
    """Rank resources by relevance to query"""
    if not resources:
        return []
    
    try:
        # Filter out resources with empty snippets
        valid_resources = [r for r in resources if r.get("snippet", "").strip()]
        
        if not valid_resources:
            logger.warning("No resources with valid snippets for ranking")
            return resources  # Return unranked if no valid snippets
        
        docs = [query] + [r["snippet"] for r in valid_resources]
        
        tfidf = TfidfVectorizer(stop_words="english")
        vectors = tfidf.fit_transform(docs)
        
        scores = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
        
        for i, r in enumerate(valid_resources):
            r["score"] = float(scores[i])
        
        # Sort by score
        ranked = sorted(valid_resources, key=lambda x: x.get("score", 0), reverse=True)
        
        logger.info(f"Ranked {len(ranked)} resources")
        return ranked
        
    except Exception as e:
        logger.error(f"Ranking failed: {e}")
        return resources  # Return unranked on error


# ---------------- Main Function ----------------
def get_resources_for_module(module_title, keywords):
    """Get top resources for a module with multiple search methods"""
    
    logger.info(f"Finding resources for: {module_title}")
    
    # Build search query
    kw_text = " ".join(keywords[:5])  # Limit keywords to avoid too long query
    query = f"{module_title} {kw_text} tutorial lecture notes"
    
    # Search web
    web_results = search_web(query, max_results=6)
    logger.info(f"Web search returned {len(web_results)} results")
    
    # Search YouTube
    yt_query = f"{module_title} tutorial"
    yt_results = search_youtube(yt_query, max_results=4)
    logger.info(f"YouTube search returned {len(yt_results)} results")
    
    # Combine results
    all_results = web_results + yt_results
    logger.info(f"Total results before ranking: {len(all_results)}")
    
    if not all_results:
        logger.warning(f"No resources found for: {module_title}")
        # Return a helpful default resource
        return [{
            "title": f"Search: {module_title}",
            "url": f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}",
            "snippet": "Click to search for resources on this topic",
            "source": "web",
            "score": 0.0
        }]
    
    # Rank and return top 5
    ranked = rank_resources(query, all_results)
    top_results = ranked[:5]
    
    logger.info(f"Returning top {len(top_results)} resources")
    
    return top_results