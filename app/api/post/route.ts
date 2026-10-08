import { hackathonSchema } from './Types';
import { prisma } from '../../../lib/prisma';
import { auth } from '@/auth';
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const session = await auth();
    console.log("incoming", body, session);

    if (!session?.user?.id) {
      return NextResponse.json({ error: "Please login to post a hackathon" }, { status: 400 });
    }

    const {
      teamName,
      hackathonName,
      regURL,
      hackathonMode,
      memberCount,
      skills,
      role,
      experience,
      regDate,
      location,
      description,
    } = body;

    const hackathon = await prisma.hackathon.create({
      data: {
        teamName,
        hackathonName,
        regURL,
        hackathonMode,
        memberCount,
        skills,
        requiredRole: role ? role.toUpperCase() : undefined,             // Mapped to schema enum field
        requiredExperience: experience ? experience.toUpperCase() : undefined, // Mapped to schema enum field
        regDate: new Date(regDate),
        location,
        description,
        userId: session.user.id,
      },
    });

    return NextResponse.json({ Hackathon: hackathon }, { status: 201 });
  } catch (error: any) {
    console.error(error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}