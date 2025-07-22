## **Frontend Build – Requirements**

### **1. Landing Website (Public)**

- Professional, clean, modern SaaS homepage.
- Clearly explain:
    - About the platform and solution (AI as an employee for business operations).
    - Services offered (automation, integration, AI operations for Finance, People Success, Payroll, IT, Engineering, etc).
    - Supported integrations and providers (e.g., Google Workspace, Office 365, AWS, Azure, Github, Jira, Firewalls, more).
    - What business use case and problems are solved (cost reduction, visibility, non-reliance, scalability, etc).
- Call to action:
    - Prominent **Login** and **Signup** buttons/links for tenant platform.
    - Sections for "Book a Demo", "Contact Us", or "Request More Info".
    - Include visually appealing hero banner, service cards, and provider logos.
    - Responsive layout and dark mode support (optional but preferred).

### **2. Tenant Platform (Secure, Auth Required)**

- After login/signup (OIDC/OAuth, e.g. Keycloak), user lands on the Tenant Dashboard.
- Main features required (all should have sidebar or tab navigation):

    1. **Account Management**
        - View and edit profile, organization/tenant details, manage users (invite, role management).

    2. **Platform Management**
        - Tenant-wide settings, audit logs, integrations (connect cloud providers, enable/disable modules).

    3. **Module Management**
        - Browse, activate/deactivate modules from a categorized marketplace (e.g., Finance, HR, IT, Security).
        - Configure modules (provider selection, settings, document upload).

    4. **Modules by Category**
        - Subsections for:
            - People Success: Payroll, Hiring
            - IT: On-premise network health, Endpoint security health, CSPM security health, Code security health, etc.

    5. **Billing Management**
        - View plans, billing history, invoices, subscription upgrades/downgrades.

    6. **Payment Management**
        - Payment method management, view/pay invoices, transaction history.

    7. **Inventory**
        - CRUD of assets/endpoints/integrations per tenant.

    8. **AI Assistant**
        - Global AI chat/help widget available across the platform for contextual assistance and Q&A.

    9. **Other Standard SaaS features**
        - Notifications (in-app and/or email), user preferences, logout, etc.

- All frontend code must be **modular, scalable, TypeScript-first**, use a modern stack (React, Next.js or Vite, shadcn/ui or Chakra/Tailwind for components).
- Use **API stubs** for all backend features, following RESTful or GraphQL conventions, ready to connect to actual services.
- Structure code for easy handoff to backend and further component development.
- Each major feature/module should be in its own folder with at least a main component and subcomponents.
- Provide a basic README in the frontend root.

---

## **Instructions for AI:**

- **Start by generating a project structure** with the required pages and folders.
- **For the landing page**, build a complete sample homepage with sample content and placeholder assets.
- **For the tenant platform**, scaffold all core pages/components, with sample navigation, authentication guard, and mock data for lists/tables.
- Use semantic HTML, accessibility best practices, and responsive CSS.
- Use only open-source libraries and frameworks.
- After generating the project structure and homepage, pause for review before generating inner pages.
- Document your assumptions and any places where backend integration will be required.

---

**End of prompt**

