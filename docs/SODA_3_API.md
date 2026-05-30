SODA3 API
 
Jordan Patrick
Last Updated: September 8, 2025 at 5:34 PM

The new SODA3 API is designed to make working with your data faster, simpler, and more reliable. With improved performance, smarter caching, and clearer error handling, it’s now easier than ever to build exactly what you need. For more technical details you can check our dev site, https://dev.socrata.com/docs/endpoints.
Here’s what you’ll notice right away:
•	Improved Performance - Our updated query endpoint provides the best performance and clearer error handling especially for complex queries.
•	Cleaner queries – No more stitching together “$” parameters. You can now write straightforward SoQL queries or send larger requests as a JSON payload.
•	Simplified results – Paging and limits are easier to manage directly within your query, reducing complexity.
•	Clearer identification – Every request now shows who is making the call, helping the system better support your use case and deliver more consistent results.
If you’re already using the SODA2.1 API, don’t worry, it’s still fully supported and will continue to be available. The default API in the platform UI will be SODA3.
SODA3 API: User Authentication Requirement
With the release of the SODA3 API, we now require user authentication or identification via app token. You can review the technical details here. For more information about creating an API key or App Token you can find our guide here
What’s Not Changing
Open Data remains open. Everyone can still access the same datasets.
What’s Changing
All new SODA3 API requests now need to identify who is making the call by including:
•	A username and password
•	An API key and secret
•	Providing an app token, if on a public dataset that doesn’t require permissions.
Why This Matters
This change protects the health, security, and stability of your open data platform. Increasingly, anonymous traffic from bots and AI scrapers puts a strain on services, creating challenges for legitimate users. By requiring requests to identify themselves, we ensure fair, reliable, and performant access for all.
What This Means for You
•	Roled site users: No real change. Just include your credentials with API requests.
•	Community users: You can still access everything for free. Simply create a free account and use those credentials when making requests.
This update ensures that open data remains accessible, reliable, and consistent even as automated traffic grows.
SODA3 Platform User Interface
With the move to SODA3, the experience for most users will feel seamless, just faster and more reliable. Tools like Exploration Canvas, Visualization, and the Overview page work the same way they used to with improved performance behind the scenes.
Export Options Update
We’ve simplified the export options to focus on the formats that provide the most value today:
CSV for Excel, CSV for Excel (Europe), and TSV for Excel → Retired. Modern Excel fully supports standard CSV files (including European formats), so everything you need is available in the single CSV option.
RDF → Retired. This legacy “semantic web” format is no longer supported by most tools.
RSS → Retired. Once popular for syndication, RSS has been replaced by modern APIs.
All commonly used export types (CSV, CSV Europe, GeoJSON, KML, KMZ, Shapefile, XLSX, and XML) remain available, ensuring the formats you rely on are still here.
Note: UI exports do not require authentication
OData with SODA3
The OData endpoint has been upgraded to SODA3, bringing the same performance and reliability improvements you’ll see across the platform.
What’s Staying the Same
You don’t need to change anything about how you use OData.
Endpoints remain the same and your existing tools and workflows will continue to work
Authentication is only required for non-Public assets
What’s New
Queries using OData will have all of the performance and reliability improvements from Soda3. 


https://dev.socrata.com/docs/endpoints