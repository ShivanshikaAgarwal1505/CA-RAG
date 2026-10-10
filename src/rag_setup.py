import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
from typing import List, Dict

class NutritionRAG:
    def __init__(self, data_path='../data/nutrition_db.csv'):
        """Initialize RAG system with nutrition database"""
        
        # Initialize ChromaDB with updated API
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="nutrition_knowledge",
            metadata={"description": "Indian food nutrition data"}
        )
        
        # Initialize embedding model
        print("Loading embedding model...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded!")
        
        # Load nutrition data
        print(f"Loading nutrition data from {data_path}...")
        self.df = pd.read_csv(data_path)
        print(f"Loaded {len(self.df)} food items")
        
    def create_searchable_text(self, row):
        """Convert food row to searchable text"""
        text = f"{row['Food Name']} ({row['Category']}): "
        text += f"Protein {row['Protein (g)']}g, "
        text += f"Iron {row['Iron (mg)']}mg, "
        text += f"Calcium {row['Calcium (mg)']}mg, "
        
        # Add biotin if present and > 0
        if pd.notna(row['Biotin (mcg)']) and row['Biotin (mcg)'] > 0:
            text += f"Biotin {row['Biotin (mcg)']}mcg, "
        
        # Add vitamin C if present and > 0
        if pd.notna(row['Vit C (mg)']) and row['Vit C (mg)'] > 0:
            text += f"Vitamin C {row['Vit C (mg)']}mg, "
        
        text += f"Calories {row['Calories']} per {row['Serving (g)']}g. "
        
        # Add context for common use cases
        if row['Protein (g)'] > 15:
            text += "High protein source. "
        if row['Iron (mg)'] > 3:
            text += "High iron content. "
        if row['Calcium (mg)'] > 100:
            text += "Good calcium source. "
        if pd.notna(row['Biotin (mcg)']) and row['Biotin (mcg)'] > 10:
            text += "Good biotin source. "
        if row['Calories'] < 100:
            text += "Low calorie option. "
            
        return text
    
    def populate_database(self):
        """Add all nutrition data to ChromaDB"""
        print("\nPopulating database...")
        
        # Check if collection already has data
        existing_count = self.collection.count()
        if existing_count > 0:
            print(f"Collection already has {existing_count} items. Clearing...")
            # Delete the collection and recreate it
            self.client.delete_collection(name="nutrition_knowledge")
            self.collection = self.client.get_or_create_collection(
                name="nutrition_knowledge",
                metadata={"description": "Indian food nutrition data"}
            )
        
        # Prepare data
        ids = []
        documents = []
        metadatas = []
        
        for idx, row in self.df.iterrows():
            # Create unique ID
            food_id = f"food_{idx}"
            ids.append(food_id)
            
            # Create searchable document
            doc_text = self.create_searchable_text(row)
            documents.append(doc_text)
            
            # Store metadata (original data)
            # Handle potential NaN values
            metadata = {
                "food_name": str(row['Food Name']),
                "category": str(row['Category']),
                "is_vegetarian": row['Category'] not in ['Animal Products', 'Seafood'],
                "protein": float(row['Protein (g)']) if pd.notna(row['Protein (g)']) else 0.0,
                "iron": float(row['Iron (mg)']) if pd.notna(row['Iron (mg)']) else 0.0,
                "calcium": float(row['Calcium (mg)']) if pd.notna(row['Calcium (mg)']) else 0.0,
                "biotin": float(row['Biotin (mcg)']) if pd.notna(row['Biotin (mcg)']) else 0.0,
                "vitamin_c": float(row['Vit C (mg)']) if pd.notna(row['Vit C (mg)']) else 0.0,
                "calories": float(row['Calories']) if pd.notna(row['Calories']) else 0.0,
                "serving": float(row['Serving (g)']) if pd.notna(row['Serving (g)']) else 100.0,
                "domain": "health"
            }
            metadatas.append(metadata)
        
        # Generate embeddings (batch for speed)
        print("Generating embeddings...")
        embeddings = self.embedder.encode(
            documents,
            show_progress_bar=True,
            batch_size=32
        ).tolist()
        
        # Add to ChromaDB in batches (ChromaDB has limits)
        batch_size = 100
        total_batches = (len(ids) + batch_size - 1) // batch_size
        
        print(f"Adding to database in {total_batches} batches...")
        for i in range(0, len(ids), batch_size):
            end_idx = min(i + batch_size, len(ids))
            print(f"  Batch {i//batch_size + 1}/{total_batches}")
            
            self.collection.add(
                ids=ids[i:end_idx],
                documents=documents[i:end_idx],
                embeddings=embeddings[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
        
        print(f"✓ Successfully added {len(ids)} food items to database!")

    def search_vegetarian(self, query: str, n_results: int = 10):
        results = self.search(query, n_results=n_results*2)  # Get extra
        # Filter for vegetarian
        veg_results = [r for r in results if r['is_vegetarian']][:n_results]
        return veg_results

    def search_nutrient(self, query: str, nutrient: str, min_value: float, n_results: int = 5):
        """Hybrid search: semantic + nutrient filtering"""
        # Get semantic results (more than needed)
        results = self.search(query, n_results=n_results*3)
    
        # Filter by actual nutrient value
        filtered = []
        for i, meta in enumerate(results['metadatas'][0]):
            if meta.get(nutrient, 0) >= min_value:
                filtered.append({
                    'metadata': meta,
                    'document': results['documents'][0][i]
                })
    
        return filtered[:n_results]

    def search(self, query: str, n_results: int = 5) -> Dict:
        """Search nutrition database using pre-computed embeddings"""
        print(f"\nSearching for: '{query}'")
        
        # Generate query embedding using our model
        query_embedding = self.embedder.encode([query]).tolist()
        
        # Search using pre-computed embedding
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        return results
    
        def display_results(self, results: Dict):
            """Pretty print search results"""
            print("\n" + "="*60)
            print("SEARCH RESULTS")
            print("="*60)
        
            if not results['documents'][0]:
                print("No results found!")
                return
        
            for i, (oc, metadata) in enumerate(zip(results['documents'][0], 
                                                  results['metadatas'][0])):
                print(f"\n{i+1}. {metadata['food_name']} ({metadata['category']})")
                print(f"   Protein: {metadata['protein']}g")
                print(f"   Iron: {metadata['iron']}mg")
                print(f"   Calcium: {metadata['calcium']}mg")
                if metadata['biotin'] > 0:
                    print(f"   Biotin: {metadata['biotin']}mcg")
                if metadata['vitamin_c'] > 0:
                    print(f"   Vitamin C: {metadata['vitamin_c']}mg")
                print(f"   Calories: {metadata['calories']} per {metadata['serving']}g")


class EducationRAG:
    def __init__(self, data_path='../data/courses_db.csv'):
        """Initialize RAG system for courses"""
        
        # FIXED: Use PersistentClient instead of Client(Settings(...))
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        self.collection = self.client.get_or_create_collection(
            name="education_knowledge",
            metadata={"description": "Course information"}
        )
        
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.df = pd.read_csv(data_path)
        print(f"Loaded {len(self.df)} courses")
    
    def create_searchable_text(self, row):
        """Convert course to searchable text"""
        text = f"{row['Course_Name']} ({row['Course_ID']}): "
        text += f"{row['Description']}. "
        text += f"Department: {row['Department']}. "
        text += f"Workload: {row['Workload_hrs_week']} hours/week. "
        text += f"Professor: {row['Prof_Name']} (GPA avg: {row['Prof_Rating_GPA']}). "
        text += f"Assessment: {row['Assessment_Type']}. "
        
        if row['Prerequisites'] != 'None':
            text += f"Prerequisites: {row['Prerequisites']}. "
        
        # Add classification
        if row['Workload_hrs_week'] < 8:
            text += "Light workload. "
        if row['Prof_Rating_GPA'] > 4.0:
            text += "High GPA professor. "
        if 'Project' in row['Assessment_Type']:
            text += "Project-based course. "
            
        return text
    
    def populate_database(self):
        """Add courses to database"""
        print("\nPopulating courses database...")
        
        # Check if already populated
        existing_count = self.collection.count()
        if existing_count > 0:
            print(f"Collection already has {existing_count} items. Clearing...")
            self.client.delete_collection(name="education_knowledge")
            self.collection = self.client.get_or_create_collection(
                name="education_knowledge",
                metadata={"description": "Course information"}
            )
        
        ids = []
        documents = []
        metadatas = []
        
        for idx, row in self.df.iterrows():
            ids.append(f"course_{idx}")
            documents.append(self.create_searchable_text(row))
            
            metadata = {
                "course_id": str(row['Course_ID']),
                "course_name": str(row['Course_Name']),
                "department": str(row['Department']),
                "prerequisites": str(row['Prerequisites']),
                "workload": float(row['Workload_hrs_week']),
                "prof_rating": float(row['Prof_Rating_GPA']),
                "assessment": str(row['Assessment_Type']),
                "difficulty": str(row['Difficulty_Level']),
                "domain": "education"
            }
            metadatas.append(metadata)
        
        print("Generating embeddings...")
        embeddings = self.embedder.encode(
            documents, 
            show_progress_bar=True,
            batch_size=32
        ).tolist()
        
        # Batch add
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            end_idx = min(i + batch_size, len(ids))
            self.collection.add(
                ids=ids[i:end_idx],
                documents=documents[i:end_idx],
                embeddings=embeddings[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
        
        print(f"✓ Added {len(ids)} courses to database!")
    
    def search(self, query: str, n_results: int = 5):
        """Search courses"""
        query_embedding = self.embedder.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        return results


class TravelRAG:
    def __init__(self, data_path='../data/travel_db.csv'):
        """Initialize RAG for travel"""
        
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        self.collection = self.client.get_or_create_collection(
            name="travel_knowledge",
            metadata={"description": "Travel destinations"}
        )
        
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # FIX: Try multiple encodings to handle special characters
        print(f"Loading travel data from {data_path}...")
        encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings_to_try:
            try:
                self.df = pd.read_csv(data_path, encoding=encoding)
                print(f"✓ Successfully loaded with {encoding} encoding")
                print(f"Loaded {len(self.df)} destinations")
                break
            except UnicodeDecodeError:
                if encoding == encodings_to_try[-1]:
                    # Last option - use errors='ignore' to skip problematic characters
                    print(f"⚠ Trying with error handling...")
                    self.df = pd.read_csv(data_path, encoding='utf-8', errors='ignore')
                    print(f"✓ Loaded {len(self.df)} destinations (some characters may be skipped)")
                else:
                    continue
    
    def create_searchable_text(self, row):
        """Convert destination to searchable text"""
        # FIX: Ensure all string values are properly cleaned
        def clean_str(val):
            """Clean string values, handle NaN and remove problematic characters"""
            if pd.isna(val):
                return ""
            return str(val).encode('ascii', 'ignore').decode('ascii')
        
        text = f"{clean_str(row['City'])}, {clean_str(row['State'])} ({clean_str(row['Type'])} destination): "
        text += f"{clean_str(row['Description'])} "
        text += f"Main attractions: {clean_str(row['Main_Attractions'])}. "
        text += f"Activities: {clean_str(row['Activities'])}. "
        text += f"Best season: {clean_str(row['Best_Season'])}. "
        
        # Handle numeric values safely
        try:
            text += f"Average cost: Rs{float(row['Avg_Cost_Per_Day']):.0f}/day. "
        except (ValueError, TypeError):
            text += f"Average cost: {clean_str(row['Avg_Cost_Per_Day'])}/day. "
        
        text += f"Recommended duration: {clean_str(row['Duration_Days_Recommended'])} days. "
        text += f"From Delhi: {clean_str(row['Transport_From_Delhi'])}, "
        
        try:
            text += f"{float(row['Distance_km']):.0f}km. "
        except (ValueError, TypeError):
            text += f"{clean_str(row['Distance_km'])}km. "
        
        # Add tags
        budget_level = clean_str(row['Budget_Level'])
        dest_type = clean_str(row['Type'])
        
        if 'Budget' in budget_level:
            text += "Budget-friendly destination. "
        if 'Luxury' in budget_level or 'Expensive' in budget_level:
            text += "Luxury destination. "
        if 'Beach' in dest_type:
            text += "Beach vacation. "
        if 'Mountain' in dest_type:
            text += "Hill station. "
        if 'Spiritual' in dest_type:
            text += "Spiritual retreat. "
        if 'Adventure' in dest_type:
            text += "Adventure destination. "
            
        return text
    
    def populate_database(self):
        """Add destinations to database"""
        print("\nPopulating travel database...")
        
        # Check if already populated
        existing_count = self.collection.count()
        if existing_count > 0:
            print(f"Collection already has {existing_count} items. Clearing...")
            self.client.delete_collection(name="travel_knowledge")
            self.collection = self.client.get_or_create_collection(
                name="travel_knowledge",
                metadata={"description": "Travel destinations"}
            )
        
        ids = []
        documents = []
        metadatas = []
        
        for idx, row in self.df.iterrows():
            ids.append(f"dest_{idx}")
            documents.append(self.create_searchable_text(row))
            
            # FIX: Handle metadata values safely
            def safe_float(val, default=0.0):
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return default
            
            def safe_str(val, default="Unknown"):
                if pd.isna(val):
                    return default
                return str(val).encode('ascii', 'ignore').decode('ascii')
            
            metadata = {
                "city": safe_str(row['City']),
                "state": safe_str(row['State']),
                "type": safe_str(row['Type']),
                "budget_level": safe_str(row['Budget_Level']),
                "avg_cost": safe_float(row['Avg_Cost_Per_Day']),
                "best_season": safe_str(row['Best_Season']),
                "duration": safe_str(row['Duration_Days_Recommended']),
                "distance_km": safe_float(row['Distance_km']),
                "domain": "travel"
            }
            metadatas.append(metadata)
        
        print("Generating embeddings...")
        embeddings = self.embedder.encode(
            documents, 
            show_progress_bar=True,
            batch_size=32
        ).tolist()
        
        # Batch add
        batch_size = 100
        total_batches = (len(ids) + batch_size - 1) // batch_size
        
        print(f"Adding to database in {total_batches} batches...")
        for i in range(0, len(ids), batch_size):
            end_idx = min(i + batch_size, len(ids))
            print(f"  Batch {i//batch_size + 1}/{total_batches}")
            
            self.collection.add(
                ids=ids[i:end_idx],
                documents=documents[i:end_idx],
                embeddings=embeddings[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
        
        print(f"✓ Added {len(ids)} destinations!")
    
    def search(self, query: str, n_results: int = 5):
        """Search destinations"""
        query_embedding = self.embedder.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        return results
    
    def display_results(self, results):
        """Pretty print travel search results"""
        print("\n" + "="*60)
        print("TRAVEL SEARCH RESULTS")
        print("="*60)
        
        if not results['documents'][0]:
            print("No results found!")
            return
        
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], 
                                                  results['metadatas'][0])):
            print(f"\n{i+1}. {metadata['city']}, {metadata['state']}")
            print(f"   Type: {metadata['type']} | Budget: {metadata['budget_level']}")
            print(f"   Cost: ₹{metadata['avg_cost']:.0f}/day | Duration: {metadata['duration']} days")
            print(f"   Distance: {metadata['distance_km']:.0f}km | Season: {metadata['best_season']}")


# MAIN EXECUTION
if __name__ == "__main__":
    print("="*60)
    print("NUTRITION RAG DATABASE SETUP")
    print("="*60)
    
    # Initialize RAG
    rag = NutritionRAG(data_path='../data/nutrition_db.csv')
    
    # Check if database already populated
    existing_count = rag.collection.count()
    if existing_count > 0:
        print(f"\n✓ Database already contains {existing_count} items")
        print("Skipping population (delete chroma_db folder to rebuild)")
    else:
        # Populate database
        rag.populate_database()
    
    # Test searches
    print("\n" + "="*60)
    print("TESTING SEARCHES")
    print("="*60)
    
    # Test 1: High protein foods
    print("\n--- Test 1: High Protein ---")
    results = rag.search("high protein vegetarian foods")
    rag.display_results(results)
    
    # Test 2: Iron-rich foods
    print("\n--- Test 2: Iron Rich ---")
    results = rag.search("iron rich foods for anemia")
    rag.display_results(results)
    
    # Test 3: Low calorie options
    print("\n--- Test 3: Low Calorie ---")
    results = rag.search("low calorie vegetables for weight loss")
    rag.display_results(results)
    
    # Test 4: Biotin (important for your cases!)
    print("\n--- Test 4: Biotin for Hair ---")
    results = rag.search("foods with biotin for hair growth")
    rag.display_results(results)
    
    # Test 5: Budget friendly
    print("\n--- Test 5: Budget Friendly ---")
    results = rag.search("cheap protein sources for students")
    rag.display_results(results)
    
    # Test 6: Calcium
    print("\n--- Test 6: Calcium for Bones ---")
    results = rag.search("calcium rich foods for bone health")
    rag.display_results(results)
    
    print("\n" + "="*60)
    print("✓ RAG database created and tested successfully!")
    print("="*60)
    
    # Show database stats
    print(f"\nDatabase contains {rag.collection.count()} food items")
    print(f"Ready for use in your constraint-aware system!")
    
    # Test education RAG
    print("\n" + "="*60)
    print("TESTING EDUCATION RAG")
    print("="*60)
    
    try:
        edu_rag = EducationRAG(data_path='../data/courses_db.csv')
        
        existing = edu_rag.collection.count()
        if existing > 0:
            print(f"✓ Education database has {existing} courses")
        else:
            edu_rag.populate_database()
        
        # Test searches
        test_queries = [
            "ML courses with high GPA professors",
            "easy courses with light workload",
            "project-based courses no exams"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            results = edu_rag.search(query, n_results=3)
            for i, meta in enumerate(results['metadatas'][0]):
                print(f"  {i+1}. {meta['course_name']}: "
                      f"Workload={meta['workload']}h, "
                      f"GPA={meta['prof_rating']}")
    except FileNotFoundError:
        print("⚠ courses_db.csv not found. Skipping education RAG.")
    except Exception as e:
        print(f"⚠ Error with education RAG: {e}")

    # Test travel RAG
    print("\n" + "="*60)
    print("TESTING TRAVEL RAG")
    print("="*60)
    
    try:
        travel_rag = TravelRAG(data_path='../data/travel_db.csv')
        
        existing = travel_rag.collection.count()
        if existing > 0:
            print(f"✓ Travel database has {existing} destinations")
        else:
            travel_rag.populate_database()

        test_queries = [
            "budget beach destinations for friends",
            "spiritual places for solo travel",
            "weekend trips from Delhi under 5000"
        ]

        for query in test_queries:
            print(f"\nQuery: {query}")
            results = travel_rag.search(query, n_results=3)
            for i, meta in enumerate(results['metadatas'][0]):
                print(f"  {i+1}. {meta['city']}: "
                      f"₹{meta['avg_cost']}/day, "
                      f"{meta['duration']} days")
    except FileNotFoundError:
        print("⚠ travel_db.csv not found. Skipping travel RAG.")
    except Exception as e:
        print(f"⚠ Error with travel RAG: {e}")
    
    print("\n" + "="*60)
    print("✓ ALL RAG DATABASES SETUP COMPLETE!")
    print("="*60)