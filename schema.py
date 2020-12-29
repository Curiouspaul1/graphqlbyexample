from models import (
    User as UserModel, Notes as NotesModel,
    session
)
from graphene import relay
import graphene
from graphene_sqlalchemy import (
    SQLAlchemyConnectionField,
    SQLAlchemyObjectType
)
from extensions import bcrypt
from typing import Optional

# types
class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node, )


class Notes(SQLAlchemyObjectType):
    class Meta:
        model = NotesModel
        interfaces = (relay.Node, )


# registeration
class createUser(graphene.Mutation):
    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        email = graphene.String()
        password = graphene.String()
    ok = graphene.Boolean()
    user = graphene.Field(User)

    def mutate(root, info, first_name, last_name, email, password):
        new_user = UserModel(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=str(
                bcrypt.generate_password_hash(password),
                'utf-8'
            )
        )
        session.add(new_user)
        session.commit()
        ok = True
        return createUser(ok=ok, user=new_user)


# add new note
class addNote(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        body = graphene.String()
    ok = graphene.Boolean()
    note = graphene.Field(Notes)

    def mutate(root, info, title, body):
        print(info.context)
        uid = info.context['uid']
        # find user based on token payload
        user = session.query(UserModel).filter_by(email=uid).first()
        new_note = NotesModel(
            title=title,
            body=body,
            user=user
        )
        session.add(new_note)
        session.commit()
        ok = True
        return addNote(ok=ok, note=new_note)


# update existing note
class updateNote(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        title = graphene.String()
        body = graphene.String()
    ok = graphene.Boolean()
    note = graphene.Field(Notes)

    def mutate(root, info, id, title: Optional[str]=None, body: Optional[str]=None):
        # find note object
        note = session.query(NotesModel).filter_by(id=id).first()
        if not title:
            note.body = body
        elif not body:
            note.title = title
        else:
            note.title = title
            note.body = body
        session.commit()
        ok = True
        note = note
        return updateNote(ok=ok, note=note)

# delete note
# get all notes
# find single note


class Query(graphene.ObjectType):
    node = relay.Node.Field()


class PreAuthQuery(graphene.ObjectType):
    node = relay.Node.Field()
    all_users = SQLAlchemyConnectionField(User)
    all_notes = SQLAlchemyConnectionField(Notes)


class PostAuthMutation(graphene.ObjectType):
    addNote = addNote.Field()
    updateNote = updateNote.Field()


class PreAuthMutation(graphene.ObjectType):
    create_user = createUser.Field()


auth_required_schema = graphene.Schema(query=Query, mutation=PostAuthMutation)
schema = graphene.Schema(query=PreAuthQuery, mutation=PreAuthMutation)
