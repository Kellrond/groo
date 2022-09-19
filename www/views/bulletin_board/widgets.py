from datetime import datetime as dt, timedelta
from re import T
from flask import session, url_for

from www         import config
from www.modules import bulletin_board as bb
from database    import bulletin_board_db
from www.modules import formatting, forms
from www.modules.widget_builder     import WidgetBuilder
from www.views.bulletin_board.forms import PostForm


class BBNavWidget(WidgetBuilder):
    def __init__(self, slug, post_id=None, outer_div='', **kwargs) -> None:
        self.slug      = slug
        self.post_id   = post_id
        self.widget_id = 'bb_nav'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        self.__get_category_details_from_slug()
        self.__generate_breadcrumbs()
        self.__set_buttons()

        inner_html = f'''
            <div id="board-header" class="row ms-2">
                <!-- Title bar and buttons -->
                <div class="row bg-warning badge text-dark d-flex">
                    <div id="left-btn" class="col-auto mt-1">{ self.left_btn }</div>
                    <div id="header-center" class="col">
                        <h4>{ self.category.get('name') }</h4>
                    </div>
                    <div id="right-btn" class="col-auto mt-1">{ self.right_btn }</div>
                </div>
                <!-- Board breadcrumbs -->
                <div class="justify-content-center d-flex"> 
                    <div id="board-heirarchy" class="d-flex mt-1 text-dark" style="font-size: 14px;">{ self.breadcrumb_html }</div>
                    <div id="sub-board-div" class="mt-1" style="font-size: 14px;">
                    <div id="board-sub-boards"></div>
                    </div>
                </div>
            </div>
        '''
        return inner_html

    def __get_category_details_from_slug(self):
        self.category = bb.returnCategoryBySlug(self.slug)
        # In case of typo send the user the home bulletin board page
        if self.category == None:
            self.category = bb.returnCategoryBySlug('bb')
        if self.category:
            self.parents = bb.returnBoardParents(self.category.get('category_id'))
            self.children = bb.returnBoardChildren(self.category.get('category_id'))
            self.subscribed = bb.isSubscribedToBoard(self.category.get('category_id'))

    def __generate_breadcrumbs(self):
        self.breadcrumb_html = ''

        for board in self.parents:
            self.breadcrumb_html += f'<div>🠜🠜&nbsp;&nbsp;<a class="text-dark text-decoration-none" href="/bulletin_board/{ board.get("slug") }">{ board.get("name") }&nbsp;&nbsp;</a></div>'

        if len(self.children) > 0:
            self.breadcrumb_html += '''
                <nav>
                    <a class="text-dark text-decoration-none" href="#" data-bs-toggle="dropdown">🠞🠞 Sub boards</a>
                    <ul class="dropdown-menu multi-level" style="font-size:14px;">'''
            
            for board in self.children:
                unread_pill = ''
                if board.get('unread_count') > 0:
                    unread_pill = f'<span class="badge rounded-pill ms-2 bg-warning text-dark" style="font-size=14px;">{ board.get("unread_count") } unread</span>'
                self.breadcrumb_html += f'''
                    <li><a class="dropdown-item" href="/bulletin_board/{ board.get('slug') }"> { '🠞' * board.get("level") }&nbsp;{ board.get('name') }</a> {unread_pill}</li>
                '''
            
            self.breadcrumb_html += '</ul></nav></div>'

        self.breadcrumb_html = '<div>' + self.breadcrumb_html[7:]

    def __set_buttons(self):
        if self.slug == None or self.slug == 'bb':
            self.left_btn = ""
            self.right_btn = ""
        elif self.post_id == None: 
            txt = "Unsubscribe" if self.subscribed else "Subscribe" 
            left_btn = forms.SubmitBtn(txt=f"<strong>{ txt }</strong>", bootstrap_color="outline-dark", _class="btn-sm")
            left_btn.addJs(onclick=f'''replaceHtml('bb_nav', '/api/change_board_subscription/', '{ self.slug }')''')
            self.left_btn  = left_btn.html()
            
            right_btn = forms.SubmitBtn(txt="<strong>New post</strong>", bootstrap_color="outline-dark", _class="btn-sm")
            right_btn.addJs(onclick=f'''replaceHtml(['bb_list','bb_post'], '/api/return_post_widget/{ self.slug }/', 'new_post')''')
            self.right_btn = right_btn.html()
        else: 
            left_btn  = forms.SubmitBtn(txt="<strong>Return to board</strong>", bootstrap_color="outline-dark", _class="btn-sm")
            left_btn.addJs(onclick=f'''location.href='/bulletin_board/{ self.slug }';''')
            self.left_btn  = left_btn.html()

            has_been_read = bb.isMsgRead(self.post_id)
            txt = "Mark unread" if has_been_read else "Mark read"
            right_btn = forms.SubmitBtn(txt=f"<strong>{ txt }</strong>", bootstrap_color="outline-dark", _class="btn-sm")
            right_btn.addJs(onclick=f'''replaceHtml('bb_nav','/api/change_unread_status/{ self.slug }/', '{ self.post_id }');''')
            self.right_btn = right_btn.html()


class BBCategoryListWidget(WidgetBuilder):
    def __init__(self, slug=None, outer_div='bb_div', **kwargs) -> None:
        self.slug = slug
        self.widget_id = 'bb_board_list'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        self.category = bb.returnCategoryBySlug(self.slug)
        self.children = bb.returnBoardChildren(self.category.get('category_id'))
        inner_html = '<div class="row mt-2 me-2">'

        for board in self.children:
            unread_pill = ''
            if board.get('unread_count') > 0:
                unread_pill = f'<span class="position-relative translate-middle badge rounded-pill bg-warning text-dark ms-5" style="font-size:10px;">{ board.get("unread_count") } unread</span>'
            spacing = '&nbsp;&nbsp;' * ((board.get('level')) * 3)

            inner_html += f'''
                <div class="col-12">
                    <a class= "text-dark text-decoration-none" href="/bulletin_board/{ board.get('slug') }">
                        <div class="row">
                            <div class="col-xl-4 col-lg-6 col-md-7 mx-3">
                                
                                <h4 class="ms-1 me-5">{ spacing }🠞 { board.get('name') }{ unread_pill }</h4>                         
                            </div>
                            <div class="col text-end"> 
                                { board.get('description') }
                            </div>                    
                        </div>                  
                    </a> 
                </div>
            '''
        return inner_html


class BBMessageListWidget(WidgetBuilder):
    def __init__(self, slug=None, outer_div='', **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.slug = slug
        self.widget_id = 'bb_list'

        self.show_active_results = True
        if kwargs.get('active') == False or kwargs.get('active') == 'False':
            self.show_active_results =  False
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        page_dict      = self.__get_pagination_dict()

        msg_cards_html = self.__return_board_msg_list_html(msg_list=page_dict.get('results'))
        pagination_links  = self.buildPaginationLinks(count=page_dict.get('count'), api_url=f'/widget/bb_category/list/{self.slug}/', api_value=self.show_active_results)

        inner_html = msg_cards_html + pagination_links

        return inner_html

    def __get_pagination_dict(self) -> dict:
        self.category = bb.returnCategoryBySlug(self.slug)
        pagination_dict = bulletin_board_db.paginateBulletinBoardMessages(board_id=self.category.get('category_id'), active=self.show_active_results, page=self.page)
        return pagination_dict

    def __return_board_msg_list_html(self, msg_list) -> list:
        inner_html = ''
        for msg in msg_list:
            if msg.get('edit_date'):
                posted_txt = f'Edited on { msg.get("edit_date").strftime(config.datetime_format) }'
            else:
                posted_txt = f'Posted on { msg.get("post_date").strftime(config.datetime_format) }'
            
            reply_txt=''
            if msg.get('latest_reply_date'):
                reply_txt = f"Last reply by { msg.get('latest_reply_by') } on { msg.get('latest_reply_date').strftime(config.datetime_format) }"

            alert = ''
            if msg.get('unread') == True:
                alert = '<span class="position-absolute top-0 start-0 translate-middle badge rounded-pill ms-2 bg-warning text-dark">Unread</span>'

            sticky = ''
            if msg.get('sticky') == True:
                sticky = '<span class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size:14px;">Sticky</span>'

            pill_formatting = 'bg-secondary text-light'
            if msg.get('author_id') == session.get('user_id'):
                pill_formatting = 'bg-warning text-dark'

            more = ''

            post_body  = formatting.htmlToPlainText(msg.get('body'))

            inner_html += f'''
                <div class="col">
                    <a class= "text-dark text-decoration-none" href="/bulletin_board/{self.slug}/{ msg.get('post_id') }">
                        <div id="msg-card-{ msg.get('post_id') }" class="card m-3 mx-5"> { alert } { sticky }
                            <div id="msg-title-post_id" class="fw-bold mx-5 mt-2"> 
                                <h4>{ msg.get('title') } </h4>
                            </div>
                            <div id="msg-text-post_id" class="row mx-4 mt-1">
                                <div class="col-2"></div>
                                <div class="col">
                                    { post_body } { more }
                                </div>
                            </div>
                            <div id="msg-footer-div" class="d-flex text-secondary">
                                <div class="col text-end fst-italic pe-2" style="font-size:12px;">
                                    <div class="ms-1 p-1" style="font-size:12px;">
                                        { posted_txt }
                                    </div>
                                    { reply_txt }
                                </div>
                            </div>
                            <span class="position-absolute top-50 start-0 translate-middle badge rounded-pill { pill_formatting } fs-small">{ msg.get('author_name') }</span>
                        </div>
                    </a>
                </div>  
                '''
        return inner_html 


class BBMessageWidget(WidgetBuilder):
    def __init__(self, slug=None, post_id=None, ext_ref_id=None, outer_div='', **kwargs) -> None:
        self.page = kwargs.get('page', 1)
        self.slug = slug
        self.post_id = post_id
        self.ext_ref_id = ext_ref_id
        self.widget_id = 'bb_msg'

        self.show_active_results = True
        if kwargs.get('active') == False or kwargs.get('active') == 'False':
            self.show_active_results =  False
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        page_dict      = self.__get_pagination_dict()
        if page_dict == None:
            return ''
        else:
            msg_cards_html = self.__return_message_html(msg_list=page_dict.get('results'))

            pagination_links  = self.buildPaginationLinks(count=page_dict.get('count'), api_url=f'/widget/bb_category/list/{self.slug}/', api_value=self.show_active_results)

            inner_html = msg_cards_html + pagination_links

            return inner_html

    def __get_pagination_dict(self) -> dict:
        self.category = bb.returnCategoryBySlug(self.slug)
        if self.ext_ref_id != None:
            self.post_id = bb.getPostIdFromExtRefId(self.slug, self.ext_ref_id)
        pagination_dict = bulletin_board_db.paginateMessage(self.post_id, self.page)
        return pagination_dict

    def __return_message_html(self, msg_list) -> list:
        inner_html = ''
        for msg in msg_list:
            # Set up title
            title = ''
            if msg.get('parent_post_id') == None \
                and msg.get("title") != None \
                and (msg.get("title") != str(msg.get('ext_ref_id')) or self.ext_ref_id == None): 
                title = f'<h2>{ msg.get("title") }</h2>'

            # # Parse msg body to HTML
            msg_html = formatting.plainTextToHtml(msg.get('body'))

            if msg.get('edit_date'):
                post_or_edit = f'Edited { msg.get("edit_date") }'
            else:
                post_or_edit = f'Posted { msg.get("post_date") }'

            author_pill_format = 'bg-warning text-dark' if msg.get('author_id') == session.get('user_id') else 'bg-dark text-light'

            # Set up pills for archive, sticky and edit
            sticky_btn  = ''
            archive_btn = ''
            edit_btn    = ''

            if msg.get('parent_post_id') == None and session.get('permissions', 0) >= config.Permissions.site_admin:
                txt = 'Unsticky' if msg.get('sticky') else 'Sticky'
                sticky_btn = forms.SubmitBtn(bootstrap_color="outline-warning", txt=txt, _id="sticky-btn", _class="btn-sm py-0 me-3")
                sticky_btn.addJs(_onclick=f'''replaceHtml('bb_msg', '/api/sticky_post/{ self.slug }/', '{ self.post_id }')''')
                sticky_btn = sticky_btn.html()

                txt = 'Archive' if msg.get('active') else 'Unarchive'
                archive_btn = f'<button id="archive-btn"  value="{ msg.get("post_id") }" type="submit">{ txt }</button>'
                archive_btn = forms.SubmitBtn(bootstrap_color="outline-secondary", txt=txt, _id="archive-btn", _class="btn-sm py-0 me-3")
                archive_btn.addJs(_onclick=f'''replaceHtml('bb_msg', '/api/archive_post/{ self.slug }/', '{ self.post_id }')''')
                archive_btn = archive_btn.html()

            if msg.get('author_id') == session.get('user_id') or session.get('permissions', 0) >= config.Permissions.site_admin:
                edit_btn = forms.SubmitBtn(bootstrap_color='outline-primary',txt="Edit", _id="edit_btn", _class="btn-sm py-0 me-3")
                if self.ext_ref_id != None:
                    post_type = 'edit_ext_ref'
                else:
                    post_type = 'edit_post' if msg.get('parent_post_id') == None else 'edit_reply'

                edit_btn.addJs(onclick=f'''replaceHtml('bb_post', '/api/return_post_widget/{ self.slug }/{ post_type }/', '{ msg.get('post_id') }')''')
                edit_btn = edit_btn.html()


            inner_html += f'''
                <div class="card col mx-5 mt-2 pt-4 px-3"> 
                    <div class="row text-center">
                    { title }
                    </div>
                    <div class="row">
                        <div class="col-1"></div>
                        <div id="msg-text-{ msg.get('post_id') }" class="col">{ msg_html }</div>
                    </div>
                    <div class="text-end mt-1 mb-2">
                        { sticky_btn }
                        { archive_btn }
                        { edit_btn }
                        <em class="ms-3" style="font-size: 13px;"> { post_or_edit }</em>
                    </div>
                    <span class="position-absolute top-50 start-0 translate-middle badge rounded-pill { author_pill_format } fs-small">{ msg.get('first_last_name') }</span>
                </div>


                '''
        return inner_html 


class BBPostWidget(WidgetBuilder):
    ''' post_type affects the text on the pill and button. Available types are 
     - new_reply
     - edit_reply
     - new_post
     - edit_post
     - ext_table'''
    def __init__(self, slug=None, post_type='new_reply', ext_ref_id=None, outer_div='', post_id=None, **kwargs) -> None:
        self.page       = kwargs.get('page', 1)
        self.slug       = slug
        self.post_id    = post_id
        self.ext_ref_id = ext_ref_id
        self.post_type  = post_type
        self.widget_id  = 'bb_post'
        super().__init__(outer_div=outer_div, **kwargs)

    def getWidgetHtml(self):
        form_action = ''
        if self.post_type == 'new_reply':
            form = PostForm(post_type=self.post_type, slug=self.slug, parent_post_id=self.post_id)
            title = ''
            pill_txt = 'New reply'
            body = form.body.html()
        elif self.post_type == 'edit_reply':
            dbo_dict = bb.returnPostById(self.post_id)
            form = PostForm(post_type=self.post_type, slug=self.slug, parent_post_id=self.post_id, post_id=self.post_id, dbo_dict=dbo_dict)
            title = ''
            pill_txt = 'Edit reply'
            body = formatting.prettyHtml(form.body.html())
        elif self.post_type == 'new_post':
            form = PostForm(post_type=self.post_type, slug=self.slug)
            title = form.title.html()
            pill_txt = 'New post'
            body = form.body.html()
        elif self.post_type == 'edit_post':
            dbo_dict = bb.returnPostById(self.post_id)
            form = PostForm(post_type=self.post_type, slug=self.slug, post_id=self.post_id, dbo_dict=dbo_dict)
            title = form.title.html()
            pill_txt = 'Edit post'
            body = formatting.prettyHtml(form.body.html())
        elif self.post_type == 'new_ext_ref':
            form = PostForm(post_type=self.post_type, slug=self.slug, ext_ref_id=self.ext_ref_id)
            form_action = f'bulletin_board/{ self.slug }'
            title = ''
            pill_txt = 'Add note'
            body = form.body.html()
        elif self.post_type == 'edit_ext_ref':
            dbo_dict = bb.returnPostById(self.post_id)
            form = PostForm(post_type=self.post_type, slug=self.slug, post_id=dbo_dict.get('post_id'), ext_ref_id=dbo_dict.get('ext_ref_id'), dbo_dict=dbo_dict)
            form_action = f'bulletin_board/{ self.slug }/{ self.post_id }'
            title = ''
            pill_txt = 'Add note'
            body = form.body.html()


        inner_html = f'''
            <div class="card col mx-5 mt-2 pt-4 px-3 mb-3"> 
                <form id="post_msg" action="{ form_action }" method="POST">
                    { form.hidden_tag_html }
                    <div class="row">
                        <div class="col-1"></div>
                        <div class="col">{ title }{ body }</div>
                    </div>
                    <div class="d-flex justify-content-end mt-3">
                        { form.submit.html() }
                    </div>
                </form>
                <span class="position-absolute top-50 start-0 translate-middle badge rounded-pill bg-warning text-dark fs-6">{ pill_txt }</span>
            </div>
            ''' 

        return inner_html