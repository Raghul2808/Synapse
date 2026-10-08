<h1 align="center" id="title">🚀 Synapse</h1>
<p align="center">
  The ultimate platform to find teammates for hackathons — globally 🌍
</p>

---

## 📌 Overview

**Synapse** is an advanced web platform designed to connect developers, designers, and enthusiasts from around the world to form high-performing hackathon teams. Leveraging strict database constraints and AI-driven matchmaking, it matches participants based on technical roles, skill stacks, and experience levels to make collaboration seamless.

---

## ✨ Features

### 👤 User & Team Features
- Secure user registration and authentication (Google & GitHub OAuth via NextAuth.js)
- Comprehensive developer profile creation and management
- AI-powered team formation using Constraint Satisfaction matching

### 🎯 Hackathon Discovery
- Explore upcoming hackathon listings across major platforms
- Advanced filters and search options
- Personalized match recommendations

### 💅 UI/UX Enhancements
- Modern responsive interface built with Tailwind CSS and Shadcn UI
- Smooth animations using Framer Motion
- Clean navigation and consistent component architecture

---

## 🛠️ Tech Stack

[![Tech Stack](https://skillicons.dev/icons?i=nextjs,ts,nodejs,tailwind,postgres,prisma,docker,vercel)](https://skillicons.dev)

- **Framework:** Next.js 14 (App Router)
- **Database & ORM:** Supabase PostgreSQL, Prisma ORM
- **Authentication:** NextAuth.js v5 (Auth.js)
- **Styling & UI:** Tailwind CSS, Shadcn UI, Framer Motion

---

## 🚀 Getting Started

### 🔄 Clone the Repository

```bash
git clone [https://github.com/Raghul2808/Synapse.git](https://github.com/Raghul2808/Synapse.git)
cd Synapse

### 📦 Install Dependencies:


npm install --legacy-peer-deps
# or
pnpm install
# or
bun install


🧪 Initialize Database & Start Server:


npx prisma db push
npx prisma generate
npm run dev
Visit http://localhost:3000 in your browser


🗂️ Project Structure
app/ — Routing and core page structure (Next.js App Router)

components/ — Reusable UI and layout components

hooks/ — Custom React hooks

lib/ — Utility libraries and helpers (Prisma client, mailers)

prisma/ — Database schema definitions and migrations

public/ — Static assets and icons



📬 Contact & Creators
Raghul M — [GitHub](https://github.com/Raghul2808) | raghul.m.2024.cse@rajalakshmi.edu.in
Rithesh Madhav S

📝 License
This project is licensed under the MIT License.






