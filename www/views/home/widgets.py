# from flask       import session, url_for
# from database    import page_content_db
# from www         import config
# from www.modules import forms
# from www.modules.widget_builder import WidgetBuilder
# from www.modules import formatting, forms
# from www.views.home.forms import HomepageContentForm


# class PostWidget(WidgetBuilder):
#     '''
#     Creates multiple widgets for posts to display
#     - Number of widgets set in app/config.py posts_on_homepage
#     '''
#     def __init__(self, outer_div='box_div height_30', **kwargs) -> None:
#         self.widget_id = 'post_content'
#         super().__init__(outer_div=outer_div, **kwargs)

#     def getWidgetHtml(self):
#         posts = page_content_db.returnHomepagePosts(self.dc.dc_id)
#         if len(posts) > 0:
#             posts_list = []
#             for post in posts:
#                 inner_html = f'''
#                     <h5 class="mt-2">{post.get('title')}</h5>
#                     <hr class="p-0 m-0" />
#                     {post.get('user_id')}
#                     <div class="mt-3">
#                         {post.get('content')}
#                     </div>
#                 '''
#                 posts_list.append(inner_html)
#             return posts_list
#         # If zero posts show a default post
#         else:
#             return f'''
#                     <h5 class="mt-2">Dc home page content</h5>
#                     <hr class="p-0 m-0" />
#                     <div class="mt-3">
#                         <p>There are no posts.</p>
#                     </div>
#             '''


# class HomePageFormWidget(WidgetBuilder):
#     def __init__(self, outer_div='box_div', **kwargs) -> None:
#         self.title = 'Home page content form'
#         self.widget_id = 'page_content_form'
#         super().__init__(outer_div=outer_div, **kwargs)

#     def getWidgetHtml(self):
#         if self.kwargs.get('page_content_id'):
#             self.kwargs['page_content'] = page_content_db.returnPageByContentId(self.kwargs.get('page_content_id'))
#         dbo_dict = self.kwargs.get('page_content')
#         form = HomepageContentForm(dbo_dict=dbo_dict)
#         inner_html = f'''
#             <h5>{ self.title }</h5>
#             <hr class="p-0 m-0" />
#             <form action="{ url_for('dc_admin.page_content_form') }" method="POST">  
#                 { form.hidden_tag_html }
#                 <div class="form-group row my-2">
#                     <div class="col-lg-8">
#                         <div class="col mt-2">
#                             { form.title.html() }
#                         </div>
#                         <div class="col mt-2">
#                             { form.content.html() }
#                         </div>
#                     </div>  
#                     <!-- Right side of form -->
#                     <div class="col-lg-4"> 
#                         <div class="mt-2">
#                             { form.publish_on.html() }
#                         </div>
#                         <div class="mt-2">
#                             { form.publish_until.html() }
#                         </div>
#                     </div>
#                 </div>
#                 <div class="d-flex justify-content-end mt-3">
#                 <div class="col d-flex mt-2">
#                     <a class="ms-2" href="https://onlinehtmleditor.dev/">HTML generator to format posts</a> 
#                     <small class="ms-2 mt-1">Enter post in text editor then click Edit HTML source code</small>
#                 </div>
#                 <div class="form-check mt-2 me-5">
#                     { form.active.html() }
#                 </div> 
#                     { form.submit_btn.html() }
#                 </div>
#             </form>
#         '''
#         return inner_html


# class HomePageListWidget(WidgetBuilder):
#     def __init__(self, outer_div='box_div', **kwargs) -> None:
#         self.page = kwargs.get('page', 1)
#         self.title = 'Home page content list'
#         self.widget_id = 'page_content_list'
#         self.dc = kwargs.get('dc')
#         self.show_active_results = True
#         if kwargs.get('active') == False or kwargs.get('active') == 'False':
#             self.show_active_results =  False
#         super().__init__(outer_div=outer_div, **kwargs)

#     def getWidgetHtml(self):
#         page_dict     = self.__get_pagination_dict()
#         content_tbl_html = self.__return_discrepancy_table_html(page_content_list=page_dict.get('results'))
#         pagination_links  = self.buildPaginationLinks(count=page_dict.get('count'), api_url='/widget/page_content/list/',api_value=self.show_active_results)

#         btn_txt = 'Show inactive' if self.show_active_results else 'Show active'
#         toggle_inactive_btn = forms.SubmitBtn(bootstrap_color='outline-dark', txt=btn_txt, _class="btn-sm ms-auto mb-2")
#         toggle_inactive_btn.addJs(_onclick=f"replaceHtml(id_to_rplc='page_content_list', api_url='/widget/page_content/list/', api_value='{ not self.show_active_results }')")

#         inner_html = f'''
#             <div class="d-flex justify-contents-between">
#                 <div>
#                     <h5>{ self.title }</h5>
#                 </div>
#                 { toggle_inactive_btn.html() }
#             </div>
#             <hr class="p-0 m-0" />
#             { content_tbl_html }
#             { pagination_links }
#         '''
#         return inner_html

#     def __get_pagination_dict(self) -> dict:
#         pagination_dict = page_content_db.paginatePageContent(dc_id=self.dc.get('dc_id'), active=self.show_active_results, page=self.page)
#         return pagination_dict

#     def __return_discrepancy_table_html(self, page_content_list) -> list:
#         html = f'''
#             <table id="home_page_table" class="table table-hover table-striped table-borderless">
#                 <tr class="overflow-hidden">
#                     <th style="width:10%;" onclick="sortTable(0, 'home_page_table')">Author</th>
#                     <th style="width:20%;" onclick="sortTable(1, 'home_page_table')">Title</th>
#                     <th style="width:36%;" onclick="sortTable(2, 'home_page_table')">Body</th>
#                     <th style="width:12%;" onclick="sortTable(3, 'home_page_table')">Shown</th>
#                     <th style="width:12%;" onclick="sortTable(4, 'home_page_table')">Until</th>
#                     <th style="width:10%;"></th>
#                 </tr>
#         '''
#         for i, post in enumerate(page_content_list):
#             edit_btn  = forms.SubmitBtn(bootstrap_color='outline-danger', txt='Edit', _class='btn-sm py-0 px-1 my-0')
#             edit_btn.addJs(_onclick=f"replaceHtml(id_to_rplc='page_content_form', api_url='/widget/page_content/form',api_value='?page_content_id={ post.get('page_content_id') }')")
#             row_id   = f'inv_disc_{ i }'
#             html += f'''
#                 <tr id="{ row_id }" class="overflow-hidden" onclick="expandTableRow(row_id='{ row_id }')">
#                     <td>{ post.get('user_id') }</td>
#                     <td>{ post.get('title') }</td>
#                     <td>{ formatting.stripAllHtml(post.get('content')) }</td>
#                     <td>{ post.get('publish_on') }</td>
#                     <td>{ post.get('publish_until') }</td>
#                     <td>{ edit_btn.html() }</td>
#                 </tr>
#             '''
#         html += '</table>'
#         return html
