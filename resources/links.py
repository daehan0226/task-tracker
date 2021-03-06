# -*- coding: utf-8 -*-
import traceback

from flask_restplus import Namespace, Resource, fields, reqparse

from core import db
from core.resource import CustomResource, response, json_serializer
from core.utils import token_required

api = Namespace('links', description='Links related operations')


def create_link(user_id, url, description, image_url):
    try:
        db.insert_link(user_id, url, description, image_url)
        return True
    except:
        traceback.print_exc()
        return False


def delete_links(ids):
    try:
        db.delete_links(ids)
        return True
    except:
        traceback.print_exc()
        return False


# https://flask-restplus.readthedocs.io/en/stable/parsing.html
parser_create = reqparse.RequestParser()
parser_create.add_argument('url', type=str, required=True, location='form', help='url')
parser_create.add_argument('description', type=str, required=True, location='form')
parser_create.add_argument('image_url', type=str, location='form')

parser_delete = reqparse.RequestParser()
parser_delete.add_argument('ids', type=str, required=True, action='split')

parser_header = reqparse.RequestParser()
parser_header.add_argument('Authorization', type=str, required=True, location='headers')

@api.route('/')
class Links(CustomResource):
    @api.doc('get all links')
    @api.expect(parser_header)
    @token_required
    def get(self, current_user, **kwargs):
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])
        links = db.get_links(user_id=current_user["uid"])
        return self.send(status=200, result=links)
    
    @api.doc('create a new link')
    @api.expect(parser_create, parser_header)
    @token_required
    def post(self, current_user, **kwargs):
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])
        args = parser_create.parse_args()
        url = args["url"]
        description = args["description"]        
        image_url = args.get("image_url")
        
        result = create_link(current_user["uid"], url, description, image_url)
        status = 201 if result else 400
        return self.send(status=status)

    @api.doc('delete links')
    @api.expect(parser_delete, parser_header)
    @token_required
    def delete(self, current_user, **kwargs):
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])
        args = parser_delete.parse_args()
        delete_links(args["ids"])
        return self.send(status=200)


@api.route('/<id_>')
@api.param('id_', 'The link identifier')
@api.response(404, 'Link not found')
class Link(CustomResource):
    @api.doc('get_link')
    @api.expect(parser_create, parser_header)
    @token_required
    def get(self, id_, current_user, **kwargs):
        '''Fetch an link given its identifier'''
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])
        try:
            link = db.get_links(id_=id_)
            if link is None:
                return self.send(status=404, result=None)
            return self.send(status=200, result=link)
        except:
            traceback.print_exc()
            return self.send(status=400, result=None)


    @api.doc('delete a link')
    @api.expect(parser_header)
    @token_required
    def delete(self, id_, current_user, **kwargs):
        '''delete a link given its identifier'''
        if current_user is None:
            return self.send(status=400, message=kwargs["error_msg"])
        try:
            delete_links([id_])
            return self.send(status=200)
        except:
            return self.send(status=400)