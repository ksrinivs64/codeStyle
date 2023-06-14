/*
 * Copyright (c) 2002 - 2006 IBM Corporation.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 */
package extractmethodrunner;

import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;

import org.eclipse.core.resources.IFile;
import org.eclipse.core.resources.IFolder;
import org.eclipse.core.resources.IProject;
import org.eclipse.core.resources.IResource;
import org.eclipse.core.resources.IWorkspace;
import org.eclipse.core.resources.ResourcesPlugin;
import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.ICoreRunnable;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.NullProgressMonitor;
import org.eclipse.equinox.app.IApplication;
import org.eclipse.equinox.app.IApplicationContext;
import org.eclipse.jdt.core.ICompilationUnit;
import org.eclipse.jdt.core.IJavaElement;
import org.eclipse.jdt.core.IJavaProject;
import org.eclipse.jdt.core.ILocalVariable;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.compiler.IProblem;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.ASTRequestor;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.CompilationUnit;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.refactoring.CompilationUnitChange;
import org.eclipse.jdt.internal.corext.refactoring.rename.RenameLocalVariableProcessor;
import org.eclipse.ltk.core.refactoring.Change;
import org.eclipse.ltk.core.refactoring.participants.CheckConditionsContext;
import org.eclipse.ltk.core.refactoring.participants.ResourceChangeChecker;
import org.eclipse.text.edits.InsertEdit;
import org.eclipse.text.edits.TextEdit;

/**
 * This class controls all aspects of the application's execution
 */
@SuppressWarnings("restriction")
public class RenameApplication implements IApplication {

	void files(IResource[] dirs, Consumer<IFile> f) throws CoreException {
		for (IResource r : dirs) {
			if (r.getType() == IResource.FILE) {
				f.accept((IFile) r);
			} else if (r.getType() == IResource.FOLDER) {
				files(((IFolder) r).members(), f);
			}
		}
	}

	@Override
	public Object start(IApplicationContext context) throws Exception {
		IProgressMonitor pm = new NullProgressMonitor();
		IWorkspace ws = ResourcesPlugin.getWorkspace();

		Map<?, ?> args = context.getArguments();
		String[] argArray = (String[]) args.get("application.args");
		int idx = 0;
		while (!"-projects".equals(argArray[idx++]))
			;
		String[] projects = argArray[idx].split(",");

		ws.run(new ICoreRunnable() {

			@Override
			public void run(IProgressMonitor monitor) throws CoreException {
				for (String project : projects) {
					IProject code = ws.getRoot().getProject(project);
					System.err.println("project at " + code.getRawLocation());
					code.open(pm);
					IJavaProject javaProject = JavaCore.create(code);
					Set<ICompilationUnit> changedFiles = new LinkedHashSet<>(); 
				
					files(code.members(), f -> {
						if (f.getName().endsWith(".java")) {
							Set<Change> renames = new LinkedHashSet<>();
							
							@SuppressWarnings("deprecation")
							final ASTParser parser = ASTParser.newParser(AST.JLS8);
							parser.setResolveBindings(true);
							parser.setProject(javaProject);
							System.err.println(f);
							ICompilationUnit icu = JavaCore.createCompilationUnitFrom(f);
							parser.createASTs(new ICompilationUnit[] { icu }, new String[0], new ASTRequestor() {
								@Override
								public void acceptAST(ICompilationUnit source, CompilationUnit ast) {
									for (IProblem p : ast.getProblems()) {
										if (p.isError()) {
											return;
										}
									}

									try {
										ast.accept(new ASTVisitor() {
											private final CheckConditionsContext checker;
											
											{ 
												checker = new CheckConditionsContext();
												checker.add(new ResourceChangeChecker());
											}

											@Override
											public boolean visit(SimpleName node) {
												visitElements(node);
												return true;
											}

											private void visitElements(ASTNode node) {
												boolean changed = false;
												try {
													for (IJavaElement elt : icu.codeSelect(
															node.getStartPosition(),
															node.getLength())) {
														if (elt instanceof ILocalVariable) {
															ILocalVariable var = (ILocalVariable) elt;
															if (! var.getElementName().equals(var.getElementName().toLowerCase())) {
																RenameLocalVariableProcessor proc = new RenameLocalVariableProcessor(var);
																proc.setNewElementName(var.getElementName().toLowerCase());
																System.err.println("trying to name " + var.getElementName());
																if (proc.checkInitialConditions(monitor).isOK()) {
																	System.err.println("initial ok for " + var.getElementName());
																	if (proc.checkFinalConditions(monitor, checker).isOK()) {
																		System.err.println("final ok for " + var.getElementName());
																		Change change = proc.createChange(monitor);
																		System.err.println("created change for " + var.getElementName());
																		renames.add(change);
																		changed = true;
																	}
																}
															}
														}
													}
												} catch (NullPointerException | CoreException e) {
													System.err.println(e);
													e.printStackTrace(System.err);
													assert false : e;
												}
												if (changed) {
													changedFiles.add(source);
												}
											}

										});
										
										if (! changedFiles.isEmpty()) {
											TextEdit edit = new InsertEdit(0, "// file changed\n");
											CompilationUnitChange c = new CompilationUnitChange("add change comment", icu);
											c.setEdit(edit);
											renames.add(c);
										}
									} catch (CoreException e) {
										System.err.println(e);
										e.printStackTrace(System.err);
										assert false : e;
									}
								}
							}, monitor);
							
							try {
								f.refreshLocal(1, monitor);
							} catch (CoreException e1) {
								System.err.println(e1);
								e1.printStackTrace(System.err);
								assert false : e1;		
							}
							
							renames.forEach(c -> { 
								try {
									c.perform(monitor);
									System.err.println("renamed " + Arrays.toString(c.getAffectedObjects()));
								} catch (CoreException e) {
									System.err.println(e);
									e.printStackTrace(System.err);
									assert false : e;		
								}
							});
						}
					});
				}
			}
		}, pm);

		ws.save(true, pm);

		return IApplication.EXIT_OK;
	}

	@Override
	public void stop() {
		// nothing to do
	}
}
