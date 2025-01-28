# Battlecard Platform

An AI-powered competitive intelligence platform for generating and managing sales battlecards.

## Core Components

### AI Agents

- **InsightsGenerationAgent**: Generates contextual insights from competitor data, market trends, and customer feedback
- **BattlecardGenerationAgent**: Creates and updates battlecards using AI-powered content generation
- **CompetitorTrackingAgent**: Monitors competitor activities and market changes in real-time

### Frontend Components

- **BattlecardWizard**: Step-by-step guided process for creating battlecards
  - Product selection
  - Competitor analysis
  - Market context
  - AI-generated content review
  
- **Role-Based Dashboards**:
  - **Sales**: Quick access to competitor updates and objection handling
  - **Marketing**: Use case management and content strategy tools
  - **Admin**: User management, integrations, and system monitoring

- **Advanced Search**: Semantic search with filters for quick access to battlecards and insights

## Getting Started

### Prerequisites

```bash
node >= 16.0.0
npm >= 8.0.0
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/battlecard-platform.git
cd battlecard-platform
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the development server:
```bash
npm run dev
```

## Usage

### Role-Based Access

The platform provides different views and capabilities based on user roles:

#### Sales Role
- View competitor updates and battlecards
- Access quick objection handling
- Generate basic battlecards

#### Marketing Role
- Manage use cases and case studies
- Review and approve battlecards
- Customize content strategy

#### Admin Role
- Manage users and permissions
- Configure data sources and integrations
- Monitor system logs and usage

### Generating Battlecards

1. Click "Create Battlecard" from the dashboard
2. Follow the wizard steps:
   - Select product line
   - Choose competitor
   - Provide market context
   - Review and customize AI-generated content

### Managing Insights

The platform automatically generates insights based on:
- Competitor activities
- Market trends
- Customer feedback
- Sales objections

Users can:
- Accept/reject insights
- View source references
- Apply insights to existing battlecards

## Error Handling

The platform implements comprehensive error handling:

- Frontend:
  - User-friendly error messages
  - Loading states with progress indicators
  - Retry mechanisms for failed operations

- Backend:
  - Detailed error logging
  - Request validation
  - Rate limiting
  - Error tracking and monitoring

## Development

### Project Structure

```
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── battlecards/
│   │   │   ├── insights/
│   │   │   └── dashboard/
│   │   ├── api/
│   │   └── contexts/
├── backend/
│   ├── agents/
│   ├── api/
│   └── services/
└── docs/
```

### Key Technologies

- Frontend:
  - React with TypeScript
  - Material-UI
  - React Query
  - Axios

- Backend:
  - Node.js/Express
  - MongoDB
  - OpenAI API
  - WebSocket for real-time updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 