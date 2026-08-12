import random
from fastapi import HTTPException,status
from uuid import uuid4,UUID
from app.models.model import Team,Bucket,Person,TeamBucket,Supervisor
from app.DB.repositories.studentrepo import StudentRepository
from app.DB.repositories.facultyrepo import FacultyRepository
from app.DB.repositories.teamstagingepo import TeamStageRepo
from app.DB.repositories.teammemberepo import TeamMembersRepo
from app.DB.repositories.projectsrepo import ProjectsRepo
class TeamService:
    def __init__(self,srepo:StudentRepository,frepo:FacultyRepository,tsrepo : TeamStageRepo,tmrepo : TeamMembersRepo,projrepo:ProjectsRepo):
        self.srepo = srepo
        self.frepo = frepo
        self.tsrepo = tsrepo
        self.tmrepo = tmrepo
        self.projrepo = projrepo
    async def _form_teams(self,dept:str,year:int,section:str,team_size:int,session_id):
        student_buckets = []
        teams = []
        team_rows = []
        student_rows = []
        count = await self.srepo.get_count(dept,year,section)
        if count == 0:
            raise HTTPException(status_code=404,detail="No Student Found in the Given Department or Year or Section")
        if team_size > count:
            raise HTTPException(status_code=400,detail="Team Size Greater Than Number of Students")
        if team_size == 0:
            raise HTTPException(status_code=400,detail="Team Size Cannot Be Zero")
        total_teams = count//team_size
        remaining_students = count % team_size
        for i in range (team_size):
            students = await self.srepo.fetch_students(dept,year,section,total_teams,total_teams*i)
            student_buckets.append(Bucket(students= students))
        for s in student_buckets[0].students:
            s.is_team_lead = True
        for _ in student_buckets:
            random.shuffle(_.students)
        for i in range (total_teams):
            members = [b.students.pop() for b in student_buckets]
            teams.append(Team(Team_id=f"{dept}_{section}_{i+1}",members=members,dept=dept,section=section)) #team_id deciding
        if remaining_students != 0:
            rows = await self.srepo.get_remaining_students(dept,year,section,remaining_students)
            for tea, row in zip(reversed(teams), rows):
                tea.members.append(Person(**dict(row)))
        for team in teams :
            team_rows.append(
                (
                team.Team_id,
                team.guide.id if team.guide else None,
                team.dept,
                team.section,
                )
            )
        for t in teams:
            for m in t.members:
                student_rows.append((
                    t.Team_id,
                    m.id,
                    m.is_team_lead
                ))
        await self.tsrepo.create_teams(team_rows,session_id)
        await self.tmrepo.add_students(student_rows)
    async def _allocate_supervisors(self,dept:str,section:list[str],session_id):
        buckets = []
        Supervisors = []
        assistants = []
        for sec in section:
            rec = await self.tsrepo.retrieve_teams(session_id,dept,sec)
            teams = [r["team_id"] for r in rec]
            buckets.append(
                TeamBucket(
                teams=teams
                )
            )
        if not any(bc.teams for bc in buckets ):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Form Teams First.")
        for _ in buckets:
            random.shuffle(_.teams)
        faculty = await self.frepo.get_faculty(dept)
        Supervisors = [Supervisor(**dict(f)) for f in faculty]
        random.shuffle(Supervisors)
        for supervisor in Supervisors:
            while not supervisor.lock and any(bu.teams for bu in buckets):
                for bucket in buckets:
                    if not bucket.teams:
                        continue
                    team_id = bucket.teams.pop()
                    supervisor.teams += 1
                    await self.tsrepo.allot_supervisor(session_id,team_id,supervisor.id)
                    if supervisor.lock:
                        break
        rem_teams = []
        for bucket in buckets:
            rem_teams.extend(bucket.teams)
        available = [sup for sup in Supervisors if not sup.lock]
        drs = [s for s in Supervisors if s.is_dr]
        result = await self.frepo.get_assistants_by_experience(dept)
        for res in result:
            assistants.append(Supervisor(**dict(res)))
        if rem_teams:
            if available:
                for supervisor in available:
                    while rem_teams and not supervisor.lock:
                        team = rem_teams.pop()
                        supervisor.teams += 1
                        await self.tsrepo.allot_supervisor(session_id,team,supervisor.id)
                        if supervisor.lock:
                                break
            if drs:
                for d in drs:
                    if rem_teams:
                        ts = rem_teams.pop()
                        await self.tsrepo.allot_supervisor(session_id,ts,d.id)
            if assistants:
                for assistant in assistants:
                    if rem_teams:
                        tm = rem_teams.pop()
                        await self.tsrepo.allot_supervisor(session_id,tm,assistant.id)
                    else :
                        break
    async def generate_teams(self,dept: str,year: int,sections: list[str],team_size: int):
        session_id = uuid4()
        for section in sections:
            await self._form_teams(dept,year,section,team_size,session_id)
        await self._allocate_supervisors(dept,sections,session_id)
        return session_id
    async def get_teams(self,session_id:UUID):
        res =  await self.tsrepo.get_teams(session_id)
        if res is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Teams Were Formed.")
        return res
    async def publish(self,session_id:UUID,dept:str):
        result = await self.get_teams(session_id)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Teams Were Formed.")
        result = [(
            res["team_id"],
            res["supervisor_id"]
        )for res in result]
        await self.projrepo.create_teams(result,dept)
        await self.tsrepo.delete_done_teams(session_id)