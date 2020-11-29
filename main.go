package main

import (
	"github.com/gin-gonic/gin"
	)

func main()  {
	router:=gin.Default()
	router.LoadHTMLGlob("templates/*.html")
	router.GET("/",func(ctx *gin.Context){
		ctx.HTML(200,"index.html",gin.H{})
	})
	router.GET("/data", func(ctx *gin.Context) {
		ctx.HTML(200,"data.html",gin.H{"data":"Helo Go/Gin World."})
	})
	router.GET("/json", func(ctx *gin.Context) {
		ctx.JSON(200,gin.H{
			"result":"200",
			"data":"Hello Gin World",
			"developer":"go lang",
		})
	})
	router.GET("/form", func(ctx *gin.Context) {
		ctx.HTML(200,"form.html",gin.H{})
	})
	router.POST("/service", func(ctx *gin.Context) {
		uname := ctx.PostForm("uname")
		ctx.JSON(200,gin.H{
			"result":"Ok",
			"hello":uname,
		})
	})
	router.GET("/main", func(ctx *gin.Context) {

	})
	router.Run(":8080")
}

