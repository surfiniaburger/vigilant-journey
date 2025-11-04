import { NextRequest, NextResponse } from 'next/server';

const AGENT_SERVER_URL = process.env.AGENT_SERVER_URL;

export async function POST(req: NextRequest) {
  console.log('Agent API route hit');
  try {
    const requestBody = await req.json();
    console.log('Request body:', requestBody);
    const { app_name, user_id, session_id } = requestBody;

    // First, try to create the session
    const sessionUrl = `${AGENT_SERVER_URL}/apps/${app_name}/users/${user_id}/sessions/${session_id}`;
    console.log('Attempting to create session at:', sessionUrl);
    const sessionResponse = await fetch(sessionUrl, {
      method: 'POST',
    });

    // If the session already exists (409), that's okay. For other errors, fail.
    if (!sessionResponse.ok && sessionResponse.status !== 409) {
      const errorText = await sessionResponse.text();
      console.error('Failed to create session:', errorText);
      return NextResponse.json({ error: 'Failed to create session', details: errorText }, { status: sessionResponse.status });
    }
    console.log(`Session creation status: ${sessionResponse.status}`);

    // Then, run the agent
    const runUrl = `${AGENT_SERVER_URL}/run`;
    console.log('Running agent at:', runUrl);
    const runResponse = await fetch(runUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!runResponse.ok) {
      const errorText = await runResponse.text();
      console.error('Failed to run agent:', errorText);
      return NextResponse.json({ error: 'Failed to run agent', details: errorText }, { status: runResponse.status });
    }

    const data = await runResponse.json();
    console.log('Agent run response:', data);
    return NextResponse.json(data);

  } catch (error) {
    console.error('Error in agent API route:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
