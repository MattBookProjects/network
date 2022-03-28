async function getCsrfToken(){
    let token = null;
    await fetch("csrf").then(response => response.json()).then(data => {token = data.token});
    return token;
}

class PostForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {content: "", app: props.app};
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
        this.setState({content: event.target.value});
    }

    handleSubmit(event) {
        if( this.state.content !== "" ){
            getCsrfToken().then(token => {
                fetch("post", {
                    method: "POST",
                    body: JSON.stringify({
                        content: this.state.content
                    }),
                    headers: {
                        "X-CSRFToken": token
                    }
                }).then(response => {
                    if(response.status === 201){
                        this.state.app.setState({page: undefined});
                        this.state.app.setState({page: <AllPosts app={this.state.app}/>})
                    }
                })
            });
        }
    }

    render(){
        return (
            <div className="post-form">
                <textarea className="post-form-content" type="text" value={this.state.content} onChange={this.handleChange} placeholder="What's up buddy?"/>
                <button className="post-form-button" onClick={this.handleSubmit}>Post</button>
            </div>
        );
    }
}

/*
function PostForm(props){
    return (
        <div>
            <textarea id="post-form-input" type="text" name="content"/>
            <button onClick={() => {
                content = document.querySelector("#post-form-input").value;
                    if( content !== ""){
                    getCsrfToken().then(token => {
                        fetch("post", {
                            method: "POST",
                            body: JSON.stringify({
                                content: content
                            }),
                            headers: {
                                "X-CSRFToken": token
                            }
                        }).then(response => {
                            if(response.status === 201){
                                props.app.setState({page: undefined});
                                props.app.setState({page: <AllPosts app={props.app}/>});
                            }
                        })
                    })
                }
            }}
                >Post
            </button>
        </div>
    );
}*/

class EditPostForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {content: props.content, field: props.field, id: props.id};
        this.handleSave = this.handleSave.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }

    handleSave(event) {
        if( this.state.content !== "" ){
            console.log(`content: ${this.state.content}`);
            getCsrfToken().then(token => {
                fetch(`posts/${this.state.id}`, {
                    method: "PUT",
                    body: JSON.stringify({
                        mode: "edit",
                        content: this.state.content
                    }),
                    headers: {
                        "X-CSRFToken": token
                    }
                }).then(response => {
                    if( response.status === 204 ){
                        this.state.field.saveEdit(this.state.content);
                    }
                })
            })
        }
    }

    handleCancel(event){
        this.state.field.cancelEdit();
    }

    handleChange(event) {
        this.setState({content: event.target.value});
    }

    render(){
        return (
            <div>
                <textarea type="text" value={this.state.content} onChange={this.handleChange}/>
                <button onClick={this.handleSave}>Save</button>
                <button onClick={this.handleCancel}>Cancel</button>
            </div>

        )
    }
}

/*
function EditPostForm(props){
    return (
        <div>
            <textarea id="edit-post-form" type="text" name="content" defaultValue={props.content}/>
            <button onClick={() => {
                content = document.querySelector("#edit-post-form").value;
                if( content !== ""){
                    getCsrfToken().then(token => {
                        fetch(`posts/${props.post.id}`, {
                            method: "PUT",
                            body: JSON.stringify({
                                mode: "edit",
                                content: content
                            }),
                            headers: {
                                "X-CSRFToken": token
                            }
                        }).then(response => {
                            if( response.status === 204 ){
                                props.field.saveEdit(content);
                            }
                        })
                    })
                }
            }}>
                Save
            </button>
        </div>
    )
}
*/

class Post extends React.Component {
    constructor(props) {
        super(props);
        this.state = {post: props.post.post, meta: props.post.meta, liked: props.post.meta.liked, likes: props.post.post.likes, app: props.app, field: props.field, content: props.content};
    }



    render(){
        let authorArea = 
            <div className="post-author-area">
                <div className="post-author" onClick={() => this.state.app.setState({page: <ProfilePage id={this.state.post.author.id} app={this.state.app} />})}>{this.state.post.author.username}</div>
             </div>   
        const mainArea = 
            <div>
                <div className="post-content">{this.state.content}</div>
                <div className="post-likes-area">Likes: {this.state.likes}</div>
            </div>;
        if (this.state.meta.authenticated){
            if (this.state.meta.owned){
                authorArea = 
                    <div className="post-author-area">
                        <div className="post-author" onClick={() => this.state.app.setState({page: <ProfilePage id={this.state.post.author.id} app={this.state.app} />})}>{this.state.post.author.username}</div>
                        <EditButton field={this.state.field}/>
                    </div>   
            }
            return (
                <div className="post">
                    {authorArea}
                    {mainArea}
                    <LikeButton id={this.state.post.id} post={this} liked={this.state.liked}/>
                </div>
            );
        }
        return (
            <div className="post">
                {authorArea}
                {mainArea}
            </div>
        );
    }
}

class PostField extends React.Component {
    constructor(props) {
        super(props);
        this.state = {page: <Post post={props.post} app={props.app} field={this} content={props.post.post.content}/>, app: props.app, post: props.post, content: props.post.post.content};
    }


    saveEdit(content){
        console.log(`content: ${content}`);
        if( content !== "" ){
            console.log("SAVE EDIT");
            this.setState({content: content, page: <Post post={this.state.post} app={this.state.app} field={this} content={content}/>});
        }
    }

    cancelEdit(){
        this.setState({page: <Post post={this.state.post} app={this.state.app} field={this} content={this.state.content}/>});
    }

    setEdit(){
        this.setState({page: <EditPostForm id={this.state.post.post.id} app={this.state.app} field={this} content={this.state.content}/>})
    }


    render(){
        return (
            <div>
                {this.state.page}
            </div>
        )
    }
}
          

  


function Posts(props){
    return (
        <div className="posts">
            {props.posts.map(post => <PostField post={post} app={props.app}/>)}
        </div>
    );
}

class AllPosts extends React.Component{
    constructor(props){
        super(props);
        this.state = { posts: undefined, app: props.app };
    }


    componentWillMount(){
        fetch("posts").then(response => response.json()).then(data => {this.setState({ posts: data})});
        fetch("profiles/me").then(response => response.json()).then(data => {this.setState({ id: data.id })});
    }

    render(){
        if (!this.state.posts){
            return (
                <div>Loading</div>
            )
        }

        if( this.state.id === null){
            return ( 
                <div>
                     <Posts posts={this.state.posts} app={this.state.app}/>
                </div>
            );
        }
        return (
            <div className="all-posts-page">
                <PostForm app={this.state.app}/>
                <Posts posts={this.state.posts} app={this.state.app}/>
            </div>
        );
    }
}

class FollowingPosts extends React.Component{
    constructor(props){
        super(props);
        this.state = { posts: undefined, app: props.app };
    }


    componentWillMount(){
        fetch("posts/following").then(response => response.json()).then(data => {this.setState({ posts: data })});
    }

    render(){
        if (!this.state.posts){
            return (
                <div>Loading</div>
            )
        }
        return (
            <div className="following-posts-page">
                <Posts posts={this.state.posts} app={this.state.app}/>
            </div>
        );
    }
}



class ProfilePage extends React.Component {
    constructor(props){
        super(props);
        this.state = { id: props.id, app: props.app };
        console.log("profile page loaded")
    }

    componentWillMount(){
        fetch(`profiles/${this.state.id}`).then(response => response.json()).then(data => {this.setState({ user: data.user, followers: data.user.followers, meta: data.meta})});
    }

    updateFollow(){
        this.setState({ })
    }

    render(){
        if (!this.state.user){
            return (
                <div>Loading</div>
            );
        }
        return (
            <div className="profile-page">
                <ProfileInfo user={this.state.user} meta={this.state.meta} followed ={this.state.meta.followed}/>
                <div className="profile-page-posts"> 
                    <Posts posts={this.state.user.posts} app={this.state.app}/>
                </div>
            </div>
        )
    }
}

class ProfileInfo extends React.Component {
    constructor(props) {
        super(props);
        this.state = { username: props.user.username, followings: props.user.followings, followers: props.user.followers, followed: props.meta.followed, id: props.user.id, meta: props.meta};
    }

    render() {
        const ret =  <div>
                        <div>username: {this.state.username}</div>
                        <div>following: {this.state.followings}</div>
                        <div>followers: {this.state.followers}</div>
                    </div>;
        if( this.state.meta.authenticated && !this.state.meta.own ) {
            return (
                <div className="profile-page-info">
                    {ret}
                    <FollowButton followed={this.state.followed} id={this.state.id} page={this}/>
                </div>
            );
        }
        return (
            <div className="profile-page-info">
                {ret}
            </div>
        );
    }
}  

class MyProfilePage extends React.Component {
    constructor(props) {
        super(props);
        this.state = { app: props.app };
    }

    componentWillMount(){
        fetch("profiles/me").then(response => response.json()).then(data => {
            console.log(data.id);
            this.setState({id: data.id});
        });
    }

    render(){
        if (!this.state.id){
            return (
                <div>Loading</div>
            );
        }
        return (<ProfilePage app={this.state.app} id={this.state.id}/>);
    }
}
  

function FollowButton(props){
        let className = "";
        if ( props.followed ){
            className = "follow-button-followed";
        } else {
            className = "follow-button-not-followed";
        }
        return (
            <button className={className} onClick={() => {
                getCsrfToken().then(token => {
                fetch(`profiles/${props.id}`,{
                    method: "PUT",
                    body: JSON.stringify({
                        follow: !props.followed
                    }),
                    headers: {
                        "X-CSRFToken": token
                    }

                }).then(response => {
                    if (response.status === 204) {
                        if( props.followed ){
                            props.page.setState({followers: props.page.state.followers - 1, followed: false});
                        } else {
                            props.page.setState({followers: props.page.state.followers + 1, followed: true});
                        }
                    }
            })})}}>
                {props.followed ? "Followed" : "Follow"}
            </button>
        );
}

function LikeButton(props) {
    return (
        <button className="like-button" onClick = {() => { 
            getCsrfToken().then(token => {
            fetch(`posts/${props.id}`, {
                method: "PUT",
                body: JSON.stringify({
                    mode: "like",
                    like: !props.liked
                }),
                headers: {
                    "X-CSRFToken": token
                }
            }).then(response => {
                if (response.status === 204){
                    if( props.liked ){
                        props.post.setState({likes: props.post.state.likes - 1, liked: false});
                    } else {
                        props.post.setState({likes: props.post.state.likes + 1, liked: true});
                    }
                }
            })
            })
        }}>
            {props.liked ? "Unlike" : "Like"}
        </button>
    );
}

function EditButton(props) {
    return(
        <button className="edit-post-button" onClick = {() => {
            props.field.setEdit();
        }}>Edit</button>
    );
}


class App extends React.Component {
    constructor(props){
        super(props);
        this.state = {page: <AllPosts app={this}/>};
        document.querySelector("#nav-all-posts").onclick = () => this.setState({page: <AllPosts app={this}/>});
        try {
            document.querySelector("#nav-following-posts").onclick = () => this.setState({page: <FollowingPosts app={this}/>});
            document.querySelector("#nav-profile").onclick = () => this.setState({page: <MyProfilePage app={this}/>});
        } catch {}

        /*if (username_element !== undefined) {
            username_element.onclick = () => this.setState({page: <MyProfilePage app={this}/>});
        } */
    }

   
 
    render(){       
        return (
            <div className="app">
                {this.state.page}
            </div>
        );
    }
}


ReactDOM.render(<App/>, document.querySelector("#app"));



//{posts.map(post => <Post author={post.author} content={post.content}/>)}


//{posts}
//{posts.map(post => <Post author={post.author} content={post.content} />)}

