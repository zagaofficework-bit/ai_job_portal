import streamlit as st
import requests
import os # Added to safely handle file paths

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Job Portal", page_icon="🚀", layout="wide")

# ==========================================
#          LOAD EXTERNAL CSS & HTML
# ==========================================
def load_css(file_name):
    """Reads a CSS file and injects it into the Streamlit app."""
    # Check if the file exists to prevent crashing
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found: {file_name}")

# Execute the function to apply your styles!
load_css("assets/style.css") 

# ==========================================
#          SESSION STATE (MEMORY)
# ==========================================
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None 

# ==========================================
#          LOGIN / REGISTER GATEWAY
# ==========================================
if st.session_state.token is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("🚀 Welcome to AI Job Portal")
        st.markdown("Join us to find your dream job or hire top talent.")
        
        login_tab, signup_tab = st.tabs(["🔒 Login", "📝 Sign Up"])
        
        with login_tab:
            st.subheader("Welcome Back")
            with st.form("login_form"):
                user_role = st.radio("Log in as:", ["Job Seeker", "HR", "Admin"], horizontal=True)
                username = st.text_input("Email / Username")
                password = st.text_input("Password", type="password")
                login_btn = st.form_submit_button("Login")
                
                if login_btn:
                    login_data = {"username": username, "password": password}
                    try:
                        res = requests.post(f"{API_URL}/auth/login", data=login_data)
                        if res.status_code == 200:
                            st.session_state.token = res.json().get("access_token")
                            st.session_state.role = user_role
                            st.success("Logged in successfully!")
                            st.rerun() 
                        else:
                            st.error("Login failed. Please check your credentials.")
                    except Exception:
                        st.error("Cannot connect to backend. Is FastAPI running?")

        with signup_tab:
            st.subheader("Create an Account")
            with st.form("register_form"):
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                new_password_confirm = st.text_input("Confirm Password", type="password")
                
                reg_btn = st.form_submit_button("Sign Up")
                
                if reg_btn:
                    if new_password != new_password_confirm:
                        st.error("Passwords do not match!")
                    else:
                        reg_data = {
                            "username": new_email, 
                            "email": new_email, 
                            "password": new_password
                        }
                        try:
                            reg_res = requests.post(f"{API_URL}/auth/register", json=reg_data)
                            if reg_res.status_code in [200, 201]:
                                st.success("Account created successfully! Switch to the Login tab to enter.")
                            else:
                                st.error(f"Registration failed: {reg_res.text}")
                        except Exception:
                            st.error("Cannot connect to backend. Is FastAPI running?")

# ==========================================
#          AUTHENTICATED DASHBOARDS
# ==========================================
else:
    with st.sidebar:
        st.success(f"✅ Logged in as: {st.session_state.role}")
        if st.button("Logout"):
            st.session_state.token = None 
            st.session_state.role = None
            st.rerun() 

    st.title(f"🚀 AI Job Portal - {st.session_state.role} Dashboard")

    # ------------------------------------------
    # ROUTE 1: JOB SEEKER VIEW
    # ------------------------------------------
    if st.session_state.role == "Job Seeker":
        st.header("🏢 Verified Companies")
        try:
            comp_response = requests.get(f"{API_URL}/companies/")
            if comp_response.status_code == 200:
                companies_list = comp_response.json()
                if companies_list:
                    for comp in companies_list:
                        with st.expander(f"{comp['name']} - {comp['industry']}"):
                            if comp.get("is_verified", False):
                                st.success("✅ **Verified Employer** - Identity Confirmed")
                            else:
                                st.warning("⚠️ **Unverified** - Proceed with caution")
                            st.write(f"**Website:** {comp['website']}")
                            st.write(f"**About:** {comp['description']}")
                else:
                    st.info("No companies registered yet.")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the backend.")

        st.divider()
        
        st.header("📋 Open Job Postings")
        if st.button("Fetch Available Jobs"):
            try:
                jobs_response = requests.get(f"{API_URL}/jobs/")
                if jobs_response.status_code == 200:
                    jobs_data = jobs_response.json()
                    if jobs_data:
                        st.dataframe(jobs_data)
                    else:
                        st.info("No jobs found. Check back later!")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the backend.")

                st.divider()

        st.header("🧠 Resume Optimizer")
        st.write("Upload your resume and paste a job description to see your match score before applying!")
        
        # We use unique keys here so Streamlit doesn't confuse this with the HR form
        candidate_job_desc = st.text_area("Target Job Description", placeholder="Paste the job description here...", key="candidate_jd")
        
        candidate_resume = st.file_uploader("Upload Your Resume (PDF/TXT)", type=['pdf', 'txt'], key="candidate_res")
        
        if st.button("Run Resume Check", type="primary", key="candidate_analyze_btn"):
            if not candidate_job_desc or not candidate_resume:
                st.warning("Please provide both a job description and your resume.")
            else:
                with st.spinner("Analyzing your resume..."):
                    # Mock backend call for UI testing
                    import random
                    mock_match = random.randint(65, 95)
                    
                    st.success("Analysis Complete!")
                    
                    # Displaying the results in a clean dashboard format
                    score_col, feedback_col = st.columns([1, 2])
                    with score_col:
                        st.metric("Your Match Score", f"{mock_match}%")
                    with feedback_col:
                        if mock_match >= 80:
                            st.info("✨ Great match! Your resume highlights the key skills needed.")
                        else:
                            st.warning("⚠️ Consider adding more keywords from the job description to improve your score.")
                
        st.divider()

        st.header("📱 Company Updates Feed")
        
        try:
            # Fetch real posts from your FastAPI database
            feed_response = requests.get(f"{API_URL}/posts/")
            
            if feed_response.status_code == 200:
                live_posts = feed_response.json()
                
                if not live_posts:
                    st.info("No company updates yet. Check back later!")
                else:
                    # Center the feed using columns
                    left_margin, feed_col, right_margin = st.columns([1, 2, 1])
                    
                    with feed_col:
                        for post in live_posts:
                            st.write("<br>", unsafe_allow_html=True)
                            
                            # Dynamically generate an avatar based on the company name
                            avatar_name = post['company_name'].replace(" ", "+")
                            avatar_url = f"https://ui-avatars.com/api/?name={avatar_name}&background=2563eb&color=fff&rounded=true"
                            
                            # 1. Post Header (Avatar + Username)
                            st.markdown(f"""
                            <div class="ig-header">
                                <img class="ig-avatar" src="{avatar_url}">
                                <span class="ig-username">{post['company_name']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 2. Post Image (Fetching the URL from FastAPI)
                            st.image(post["image_url"], use_container_width=True)
                            
                           # 3. Action Icons (Now fully functional!)
                            btn1, btn2, btn3, empty_space = st.columns([1, 1, 2, 4])
                            
                            with btn1:
                                if st.button("🤍", key=f"like_{post['id']}"):
                                    try:
                                        like_res = requests.post(f"{API_URL}/posts/{post['id']}/like")
                                        if like_res.status_code == 200:
                                            st.rerun() # Refreshes page to show new like count
                                    except Exception:
                                        st.error("Connection failed.")
                                        
                            with btn2:
                                if st.button("💬", key=f"comment_{post['id']}"):
                                    st.session_state[f"show_comments_{post['id']}"] = not st.session_state.get(f"show_comments_{post['id']}", False)
                                    
                            with btn3:
                                if st.button("🚀 Apply", key=f"apply_{post['id']}"):
                                    st.success(f"Application sent to {post['company_name']}!")
                            
                            # Optional: Comment box toggle expansion
                            if st.session_state.get(f"show_comments_{post['id']}", False):
                                comment_text = st.text_input("Write a comment...", key=f"comment_input_{post['id']}")
                                if st.button("Post Comment", key=f"submit_comment_{post['id']}"):
                                    st.success("Comment added!")
                            
                            # 4. Likes & Caption
                            st.markdown(f"""
                            <div class="ig-caption-box">
                                <div style="font-weight: 600; margin-bottom: 4px;">{post.get('likes', 0)} likes</div>
                                <span class="ig-bold">{post['company_name']}</span>
                                <span>{post['caption']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Divider between posts
                            st.markdown("<hr style='border:1px solid #262626; margin-top: 24px;'>", unsafe_allow_html=True)
            else:
                st.error("Failed to load feed.")
        except Exception:
            st.error("Cannot connect to the backend. Is FastAPI running?")

    # ------------------------------------------
    # ROUTE 2: HR VIEW
    # ------------------------------------------
    elif st.session_state.role == "HR":
        st.header("🏢 Register a New Company")
        with st.form("new_company_form", clear_on_submit=True):
            name = st.text_input("Company Name", placeholder="e.g. Zaga Soft")
            industry = st.text_input("Industry", placeholder="e.g. Information Technology")
            website = st.text_input("Company Website", placeholder="e.g. https://zagasoft.com")
            registration_id = st.text_input("Registration ID (CIN/GSTIN/EIN)", placeholder="e.g. U72200MH2020PTC331234")
            official_email = st.text_input("Official HR/Admin Email", placeholder="e.g. careers@zagasoft.com")
            description = st.text_area("Company Description")
            
            company_submitted = st.form_submit_button("Register Company")
            
            if company_submitted:
                new_company_data = {
                    "name": name,
                    "industry": industry,
                    "website": website,
                    "registration_id": registration_id,
                    "official_email": official_email,
                    "description": description
                }
                try:
                    comp_response = requests.post(f"{API_URL}/companies/", json=new_company_data)
                    if comp_response.status_code == 200:
                        created_company = comp_response.json()
                        st.success(f"Company Registered! Your ID is: {created_company['id']}")
                        st.info("Save this ID! You will need it to post jobs below.")
                    else:
                        st.error(f"Error registering company: {comp_response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to the backend.")
                    
        st.divider()

        st.header("➕ Post a New Job")
        with st.form("new_job_form", clear_on_submit=True):
            title = st.text_input("Job Title", placeholder="e.g. Senior Data Scientist")
            description = st.text_area("Job Description", placeholder="Describe the role...")
            skills_input = st.text_input("Required Skills (comma-separated)", placeholder="Python, FastAPI, MongoDB")
            experience_years = st.number_input("Years of Experience Required", min_value=0, step=1)
            company_id = st.text_input("Company ID", help="Paste your Zaga Soft ID here")
            
            submitted = st.form_submit_button("Submit Job Posting")
            
            if submitted:
                new_job_data = {
                    "title": title,
                    "description": description,
                    "skills_required": [skill.strip() for skill in skills_input.split(",") if skill.strip()],
                    "experience_years": experience_years,
                    "company_id": company_id
                }
                try:
                    post_response = requests.post(f"{API_URL}/jobs/", json=new_job_data)
                    if post_response.status_code == 200:
                        st.success("Job successfully posted!")
                    else:
                        st.error(f"Error posting job: {post_response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to the backend. Is your FastAPI server running?")

        st.divider()

        st.subheader("🧠 ATS Batch Resume Screener")
        st.write("Upload multiple candidate resumes to instantly rank them against the job description.")

        job_description = st.text_area("Target Job Description", placeholder="Paste the job requirements here...")

        # 1. Enable multiple file uploads
        uploaded_files = st.file_uploader(
            "Upload Candidate Resumes (PDF/TXT)", 
            type=['pdf', 'txt'], 
            accept_multiple_files=True # This is the magic toggle
        )

        if st.button("Run Batch Analysis", type="primary"):
            if not job_description or not uploaded_files:
                st.warning("Please provide a job description and at least one resume.")
            else:
                with st.spinner(f"Analyzing {len(uploaded_files)} resumes..."):
                    
                    # We will store the results in a list so we can sort them later
                    ranked_results = []
                    
                    for file in uploaded_files:
                        # 2. In a real scenario, you would send 'file' to your FastAPI backend here
                        # response = requests.post(f"{API_URL}/analyze", files={"file": file}, data={"jd": job_description})
                        # score = response.json().get("score")
                        
                        # For this UI demonstration, we will generate a mock score
                        import random
                        mock_score = random.randint(40, 98) 
                        
                        ranked_results.append({
                            "Candidate File": file.name,
                            "Match Score": mock_score,
                            "Status": "Shortlisted" if mock_score >= 75 else "Rejected"
                        })
                    
                    # 3. Sort the results from highest score to lowest (The Ranking Algorithm)
                    ranked_results = sorted(ranked_results, key=lambda x: x["Match Score"], reverse=True)
                    
                    # 4. Display the results in a clean Leaderboard Table
                    st.success("Analysis Complete! Here is your shortlisted leaderboard:")
                    st.dataframe(
                        ranked_results,
                        column_config={
                            "Match Score": st.column_config.ProgressColumn(
                                "Match Score",
                                help="AI Compatibility Score",
                                format="%d%%",
                                min_value=0,
                                max_value=100,
                            ),
                            "Status": st.column_config.TextColumn("Status")
                        },
                        hide_index=True,
                        use_container_width=True
                    )

        st.divider()
        
        st.header("📸 Create a Company Post")
        st.markdown("Share company culture photos or visual job announcements!")

        with st.form("new_social_post", clear_on_submit=True):
            # We added Company Name because your FastAPI backend requires it!
            company_name = st.text_input("Company Name", placeholder="e.g. Zaga Soft")
            
            post_text = st.text_area(
                "Caption", 
                placeholder="e.g., We just had an amazing team lunch! Also, we are hiring a new UI Designer! 👇"
            )
            post_image = st.file_uploader("Upload a Company Photo", type=["png", "jpg", "jpeg"])
            
            submit_post = st.form_submit_button("Publish Post")
            
            if submit_post:
                if not company_name:
                    st.warning("Please provide your Company Name.")
                elif not post_image:
                    st.warning("Please upload an image for the post.")
                else:
                    with st.spinner("Publishing post..."):
                        try:
                            # 1. Package the text data for FastAPI Form(...)
                            data_payload = {
                                "caption": post_text,
                                "company_name": company_name
                            }
                            
                            # 2. Package the image for FastAPI File(...)
                            # We use .getvalue() to read the raw bytes of the image from Streamlit
                            file_payload = {
                                "file": (post_image.name, post_image.getvalue(), post_image.type)
                            }
                            
                            # 3. Send the POST request to our new endpoint
                            res = requests.post(f"{API_URL}/posts/", data=data_payload, files=file_payload)
                            
                            if res.status_code == 200:
                                st.success("✅ Post published successfully to the live feed!")
                            else:
                                st.error(f"Failed to publish post: {res.text}")
                        
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to backend. Is FastAPI running?")

    # ------------------------------------------
    # ROUTE 3: ADMIN VIEW
    # ------------------------------------------
    elif st.session_state.role == "Admin":
        st.header("👑 Admin Control Panel")

        admin_tab1, admin_tab2 = st.tabs(["Verify Companies", "Manage Users"])
        
        with admin_tab1:
            st.subheader("Pending Company Approvals")
            
            try:
                # Ask FastAPI for a list of unverified companies
                res = requests.get(f"{API_URL}/companies/pending")
                
                if res.status_code == 200:
                    pending_companies = res.json()
                    
                    if not pending_companies:
                        st.success("No pending approvals! You are all caught up.")
                    else:
                        # Loop through the list and create a button for each one
                        for comp in pending_companies:
                            st.write(f"**{comp['name']}** - {comp['industry']}")
                            
                            # Unique key for every button so Streamlit doesn't get confused
                            if st.button(f"Approve {comp['name']}", key=f"approve_{comp['id']}"):
                                
                                # Send the PUT request to FastAPI to update MongoDB
                                verify_res = requests.put(f"{API_URL}/admin/companies/{comp['id']}/verify")
                                
                                if verify_res.status_code == 200:
                                    st.success(f"✅ {comp['name']} has been approved!")
                                    st.rerun() # Refresh the page immediately
                                else:
                                    st.error(f"Failed to approve: {verify_res.text}")
                else:
                    st.warning("Could not fetch pending companies. Check backend logs.")
                    
            except Exception:
                st.error("Cannot connect to backend. Is FastAPI running?")
            
        with admin_tab2:
            st.subheader("Platform Statistics")
            
            try:
                # Fetch real stats from FastAPI
                stats_res = requests.get(f"{API_URL}/admin/stats")
                
                if stats_res.status_code == 200:
                    stats = stats_res.json()
                    
                    col1, col2, col3 = st.columns(3)
                    
                    # Display the real data (or 0 if the database is empty)
                    col1.metric("Total Registered Users", stats.get("total_users", 0))
                    col2.metric("Active Job Posts", stats.get("active_job_posts", 0))
                    
                    # You can add more metrics here as your database grows!
                    col3.metric("System Status", "Online 🟢")
                    
                else:
                    st.warning("Could not fetch platform statistics.")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Is FastAPI running?")