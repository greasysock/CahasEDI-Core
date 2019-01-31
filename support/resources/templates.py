import falcon, json
from support.edi import stream_handle


class Templates:
    def on_get(self, req, resp):
        out_list = list()
        for template in stream_handle.template_operators.template_list:
            out = dict()
            out['id'] = template.identifier_code
            out['description'] = template.description
            out_list.append(out)

        resp.body = json.dumps(out_list, indent=2)
        resp.status = falcon.HTTP_200


class Template:
    def on_get(self, req, resp, template_id):
        for template in stream_handle.template_operators.template_list:
            if template.identifier_code == int(template_id):
                t = template.get_template()
                t = t()
                details = t.get_detailed_structure()
                if details:
                    resp.body = json.dumps(details, indent=2)
                else:
                    resp.status = falcon.HTTP_400
                break
