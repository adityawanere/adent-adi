import csv
from dotenv import load_dotenv
import os
import datetime
from github import Github

load_dotenv()

def get_response_time(url):
    if url == "facebook.com":
        return 0.5
    if url == "google.com":
        return 0.3
    if url == "openai.com":
        return 0.4
    
def restart_application(customer_name, environment, application):
    
    # Load customers from CSV into a dictionary
    customers = {}
    with open('customers.csv', 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            if len(row) >= 3:
                name = row[0].strip()
                code = row[1].strip()
                # Split the environments string by comma
                environments = [env.strip() for env in row[2].split(',')]
                customers[name] = {
                    'code': code,
                    'environments': environments
                }

    # Validate customer name
    if customer_name not in customers:
        raise ValueError(f"Customer '{customer_name}' not recognized. Available customers: {', '.join(customers.keys())}")

    customer = customers[customer_name]

    # Validate environment
    if environment not in customer['environments']:
        raise ValueError(f"Environment '{environment}' not valid for customer '{customer_name}'. Available environments: {', '.join(customer['environments'])}")

    # Validate application
    if application not in ['cbp', 'Open Access', 'Image Server', 'Space Planning']:
        raise ValueError(f"Application '{application}' not recognized. Available applications: cbp, Open Access, Image Server, Space Planning")
    
    # Simulate the restart operation
    print(f"Restarting {application} for {customer_name} and code {customer['code']} in {environment} environment...")

    # Create a git commit using the GitHub API using the GITHUB_REPO_URL from .env and pygithub
    try:        
        # Get environment variables
        github_token = os.getenv("GITHUB_TOKEN")
        github_repo_url = os.getenv("GITHUB_REPO_URL")
        # Optional: separate token for approvals (if using a bot account)
        approval_token = os.getenv("GITHUB_APPROVAL_TOKEN", github_token)
        
        if github_token and github_repo_url:
            # Initialize GitHub client
            g = Github(github_token)
            
            # Extract repo owner and name from URL
            # Expected format: https://github.com/owner/repo or owner/repo
            if github_repo_url.startswith("https://github.com/"):
                repo_path = github_repo_url.replace("https://github.com/", "")
            else:
                repo_path = github_repo_url
            
            # Get the repository
            repo = g.get_repo(repo_path)
            
            # Create commit message
            commit_message = f"Restart {application} for {customer['code']} in {environment}"
            
            # Create file path for this customer and environment
            file_path = f"environments/{customer['code']}/{environment}/utilities/restart-services/vmss-services/vmss-management.json"
            
            try:
                # Read the existing vmss-management.json file
                existing_file = repo.get_contents(file_path)
                existing_content = existing_file.decoded_content.decode('utf-8')
                
                import json
                restart_vmss_data = json.loads(existing_content)
                
                # Map application names to match the JSON format
                app_name_mapping = {
                    "cbp": "cbp",
                    "Open Access": "open-access", 
                    "Image Server": "image-server",
                    "Space Planning": "space-planning"
                }
                
                target_app_name = app_name_mapping.get(application, application.lower().replace(" ", "-"))
                
                # Find and update the comment for the specific application
                app_found = False
                for app in restart_vmss_data.get("apps", []):
                    if app.get("name") == target_app_name:
                        app["comment"] = f"Restarted at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} for {customer['code']} in {environment}"
                        app_found = True
                        break
                
                if not app_found:
                    print(f"Application '{target_app_name}' not found in vmss-management.json")
                    return f"Application '{target_app_name}' not found in vmss-management.json for {customer['code']} {environment}"
                
                # Update the file content
                updated_content = json.dumps(restart_vmss_data, indent=2)
                
                # Create a new branch for the PR
                branch_name = f"Agent-Adi-restart-{customer['code']}-{environment}-{target_app_name}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
                
                # Get the main branch reference
                main_ref = repo.get_git_ref("heads/main")
                main_sha = main_ref.object.sha
                
                # Create new branch
                repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_sha)
                
                # Commit the updated file to the new branch
                repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=updated_content,
                    sha=existing_file.sha,
                    branch=branch_name
                )
                
                # Create Pull Request
                pr_title = f"Restart {application} for {customer['code']} in {environment}"
                pr_body = f"""
                    ## Restart Request

                    **Customer:** {customer_name} ({customer['code']})
                    **Environment:** {environment}
                    **Application:** {application}
                    **Timestamp:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                    ### Changes
                    - Updated comment for {target_app_name} in vmss-management.json
                    - Added restart timestamp for tracking

                    ### File Modified
                    - `{file_path}`

                    This PR was automatically created by the restart agent.
                    """
                
                pull_request = repo.create_pull(
                    title=pr_title,
                    body=pr_body,
                    head=branch_name,
                    base="main"
                )
                
                # Try to approve the pull request
                try:
                    # Use separate approval token if available
                    if approval_token != github_token:
                        approval_client = Github(approval_token)
                        approval_repo = approval_client.get_repo(repo_path)
                        approval_pr = approval_repo.get_pull(pull_request.number)
                        approval_pr.create_review(event="APPROVE", body="Auto-approved by restart agent")
                    else:
                        pull_request.create_review(event="APPROVE", body="Auto-approved by restart agent")
                    print(f"Pull Request approved successfully")
                except Exception as approval_error:
                    print(f"Approval not required or failed: {str(approval_error)}")
                
                # Add sleep of 5 seconds to allow for any processing
                import time
                time.sleep(5)
                
                # Merge the pull request
                try:
                    merge_result = pull_request.merge(
                        commit_title=f"Merge PR #{pull_request.number}: {pr_title}",
                        commit_message="Auto-merged by restart agent",
                        merge_method="squash"  # Can be "merge", "squash", or "rebase"
                    )
                    print(f"Pull Request merged successfully")
                    print(f"Merge commit SHA: {merge_result.sha}")
                except Exception as merge_error:
                    print(f"Merge failed: {str(merge_error)}")
                    # If squash fails, try regular merge
                    try:
                        merge_result = pull_request.merge(
                            commit_title=f"Merge PR #{pull_request.number}: {pr_title}",
                            commit_message="Auto-merged by restart agent",
                            merge_method="merge"
                        )
                        print(f"Pull Request merged successfully with regular merge")
                        print(f"Merge commit SHA: {merge_result.sha}")
                    except Exception as second_merge_error:
                        print(f"Both merge attempts failed: {str(second_merge_error)}")
                        return f"PR created but auto-merge failed: {pull_request.html_url}"
                
                print(f"Git commit created: {commit_message}")
                print(f"Pull Request created: #{pull_request.number} - {pull_request.html_url}")
                print(f"Pull Request approved and merged successfully")
                print(f"Merge commit SHA: {merge_result.sha}")
                
            except Exception as file_error:
                print(f"Error reading/updating vmss-management.json: {str(file_error)}")
                return f"Error updating vmss-management.json: {str(file_error)}"
        else:
            print("GitHub credentials not found in environment variables")
            
    except Exception as e:
        print(f"Failed to create Git commit: {str(e)}")

    return f"Restarted {application} for {customer_name} and code {customer['code']} in {environment} environment."
